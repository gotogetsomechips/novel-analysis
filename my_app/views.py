from django.db.models import Count
from django.shortcuts import render
from .models import Novel


def novel_list(request, list_name=None, type_name=None):
    # 获取所有小说
    novels = Novel.objects.all()

    # 根据 list_name 和 type_name 过滤小说列表
    if list_name:
        novels = novels.filter(list=list_name)
    if type_name:
        novels = novels.filter(type=type_name)

    # 分页
    from django.core.paginator import Paginator
    paginator = Paginator(novels, 12)  # 每页12个小说
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 获取所有类别和榜单类型，以便在侧边栏显示
    types = Novel.objects.values('type').distinct()
    lists = Novel.objects.values('list').distinct()

    return render(request, 'novel_list.html', {
        'page_obj': page_obj,
        'types': types,
        'lists': lists,
        'current_list': list_name,
        'current_type': type_name,
    })


def novel_type_statistics(request):
    # 统计数据库中的type字段
    type_counts = Novel.objects.values('type').annotate(type_count=Count('type')).order_by('-type_count')

    # 提取类型名称和对应数量
    legend_data = [item['type'] for item in type_counts]
    series_data = [{'name': item['type'], 'value': item['type_count']} for item in type_counts]

    return render(request, 'novel_type_statistics.html', {
        'legend_data': legend_data,
        'series_data': series_data,
    })


def novel_people_statistics(request):
    # 获取所有人的观看人数
    people_data = Novel.objects.values('people')

    # 对people字段进行预处理，分配到每5万一个区间，达到30万时变成"30万以上"
    intervals = {
        '5万以下': 0,
        '5-10万': 0,
        '10-15万': 0,
        '15-20万': 0,
        '20-25万': 0,
        '25-30万': 0,
        '30万以上': 0,
    }

    # 对每个观看人数进行分配
    for person in people_data:
        try:
            people_count = int(person['people'])  # 确保转换为整数
        except ValueError:
            continue  # 如果转换失败，跳过该条记录
        if people_count < 50000:
            intervals['5万以下'] += 1
        elif 50000 <= people_count < 100000:
            intervals['5-10万'] += 1
        elif 100000 <= people_count < 150000:
            intervals['10-15万'] += 1
        elif 150000 <= people_count < 200000:
            intervals['15-20万'] += 1
        elif 200000 <= people_count < 250000:
            intervals['20-25万'] += 1
        elif 250000 <= people_count < 300000:
            intervals['25-30万'] += 1
        else:
            intervals['30万以上'] += 1

    # 转换为前端所需的数据格式
    interval_labels = list(intervals.keys())
    interval_counts = list(intervals.values())

    # 将数据传递给模板
    return render(request, 'novel_people_statistics.html', {
        'legend_data': interval_labels,
        'series_data': [{'name': label, 'value': count} for label, count in zip(interval_labels, interval_counts)],
    })
from django.db.models import Count
from django.shortcuts import render
from .models import Novel

def novel_chapter_statistics(request):
    # 获取所有小说的章节数
    chapter_data = Novel.objects.values('chapter')

    # 对章节数进行预处理，分配到每200一条，1000以上归为"1000以上"
    intervals = {
        '200以下': 0,
        '200-400': 0,
        '400-600': 0,
        '600-800': 0,
        '800-1000': 0,
        '1000以上': 0,
    }

    # 对每个章节数进行分配
    for novel in chapter_data:
        try:
            chapter_count = int(novel['chapter'])  # 确保转换为整数
        except ValueError:
            continue  # 如果转换失败，跳过该条记录
        if chapter_count < 200:
            intervals['200以下'] += 1
        elif 200 <= chapter_count < 400:
            intervals['200-400'] += 1
        elif 400 <= chapter_count < 600:
            intervals['400-600'] += 1
        elif 600 <= chapter_count < 800:
            intervals['600-800'] += 1
        elif 800 <= chapter_count < 1000:
            intervals['800-1000'] += 1
        else:
            intervals['1000以上'] += 1

    # 转换为前端所需的数据格式
    interval_labels = list(intervals.keys())
    interval_counts = list(intervals.values())

    # 将数据传递给模板
    return render(request, 'novel_chapter_statistics.html', {
        'legend_data': interval_labels,
        'series_data': [{'name': label, 'value': count} for label, count in zip(interval_labels, interval_counts)],
    })


def get_recommended_novels_by_type(request, type_name=None):
    """根据类型获取推荐小说"""

    # 特殊处理的类型（从四个榜单各取前3）
    special_types = ['科幻末世', '游戏体育', '悬疑脑洞']
    # 男频专属类型（从男频榜单各取前6）
    male_types = ['都市日常', '都市修真', '都市高武', '奇幻仙侠', '历史古代',
                  '战神赘婿', '都市种田', '传统玄幻', '历史脑洞', '都市脑洞',
                  '玄幻脑洞', '悬疑灵异', '抗战谍战', '动漫衍生', '男频衍生']
    # 女频专属类型（从女频榜单各取前6）
    female_types = ['女频衍生', '玄幻言情', '种田', '年代', '现言脑洞', '宫斗宅斗',
                    '古言脑洞', '医术', '快穿', '青春甜宠', '星光璀璨', '悬疑恋爱',
                    '职场婚恋', '豪门总裁', '民国言情']

    novels = []

    if type_name:
        if type_name in special_types:
            # 从四个榜单各取前3
            lists = ['男频阅读榜', '男频新书榜', '女频阅读榜', '女频新书榜']
            for list_name in lists:
                top_novels = Novel.objects.filter(
                    list=list_name,
                    type=type_name
                ).order_by('sort')[:3]
                novels.extend(top_novels)

        elif type_name in male_types:
            # 从男频榜单各取前6
            lists = ['男频阅读榜', '男频新书榜']
            for list_name in lists:
                top_novels = Novel.objects.filter(
                    list=list_name,
                    type=type_name
                ).order_by('sort')[:6]
                novels.extend(top_novels)

        elif type_name in female_types:
            # 从女频榜单各取前6
            lists = ['女频阅读榜', '女频新书榜']
            for list_name in lists:
                top_novels = Novel.objects.filter(
                    list=list_name,
                    type=type_name
                ).order_by('sort')[:6]
                novels.extend(top_novels)

    # 分页
    from django.core.paginator import Paginator
    paginator = Paginator(novels, 12)  # 每页12本小说
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 获取所有类别和榜单类型
    types = Novel.objects.values('type').distinct()
    lists = Novel.objects.values('list').distinct()

    return render(request, 'novel_list.html', {
        'page_obj': page_obj,
        'types': types,
        'lists': lists,
        'current_type': type_name,
        'is_recommended': True
    })