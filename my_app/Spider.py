import requests
from bs4 import BeautifulSoup
import time
import re
import pymysql
from pymysql.err import Error

# 类型映射字典
CATEGORY_MAPPING = {
    '8': '科幻末世',
    '746': '游戏体育',
    '1015': '女频衍生',
    '248': '玄幻言情',
    '23': '种田',
    '79': '年代',
    '267': '现言脑洞',
    '246': '宫斗宅斗',
    '539': '悬疑脑洞',
    '253': '古言脑洞',
    '247': '医术',
    '24': '快穿',
    '749': '青春甜宠',
    '745': '星光璀璨',
    '747': '悬疑恋爱',
    '750': '职场婚恋',
    '748': '豪门总裁',
    '1017': '民国言情'
}


def connect_to_database():
    """
    连接到MySQL数据库
    :return: 数据库连接对象
    """
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='novel',
            charset='utf8mb4'
        )
        print("成功连接到MySQL数据库")
        return connection
    except Error as e:
        print(f"连接数据库时发生错误: {e}")
        return None


def save_to_database(novels, connection):
    """
    将小说数据保存到MySQL数据库
    :param novels: 小说数据列表
    :param connection: 数据库连接对象
    """
    try:
        with connection.cursor() as cursor:
            insert_query = """
            INSERT INTO novel (title, author, status, people, chapter, img, sort, type, list)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            for novel in novels:
                data_tuple = (
                    novel['书名'],
                    novel['作者'],
                    novel['状态'],
                    novel['阅读量'],
                    novel['章节数'],
                    novel['封面图片'],
                    novel['排名'],
                    novel['类型'],
                    novel['榜单']
                )

                cursor.execute(insert_query, data_tuple)
                print(f"已插入《{novel['书名']}》的数据")

            connection.commit()
            print("所有数据已成功保存到数据库")

    except Error as e:
        print(f"保存数据时发生错误: {e}")
        connection.rollback()


def get_novel_list(page=1, category_id='8'):
    """
    获取番茄小说排行榜数据
    :param page: 页码，默认第1页
    :param category_id: 类型ID
    :return: 处理后的小说列表数据
    """
    offset = (page - 1) * 10

    rank_url = "https://fanqienovel.com/api/rank/category/list"
    params = {
        "app_id": "1967",
        "rank_list_type": "3",
        "offset": str(offset),
        "limit": "10",
        "category_id": category_id,
        "rank_version": "",
        "gender": "0",
        "rankMold": "1",
        "msToken": "",
        "a_bogus": ""
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'cookie': '',
        'refer': 'https://fanqienovel.com/rank/1_2_261'
    }

    try:
        print(f"正在获取 {CATEGORY_MAPPING[category_id]} 类型第{page}页数据...")
        response = requests.get(rank_url, params=params, headers=headers)

        data = response.json()
        processed_novels = []
        for novel in data.get('data', {}).get('book_list', []):
            novel_url = f"https://fanqienovel.com/page/{novel['bookId']}?enter_from=Rank"
            print(f"正在获取小说《{novel.get('bookName', '')}》的详细信息...")
            novel_response = requests.get(novel_url, headers=headers)
            soup = BeautifulSoup(novel_response.text, 'html.parser')

            chapter_text = soup.select_one('div.page-directory-header h3').text if soup.select_one(
                'div.page-directory-header h3') else ''
            chapter_number = re.search(r'\d+', chapter_text)
            chapter_count = int(chapter_number.group()) if chapter_number else 0

            processed_novel = {
                '排名': novel.get('currentPos'),
                '阅读量': novel.get('read_count'),
                '封面图片': novel.get('thumbUri', '').replace('\u0026', '&'),
                '书名': soup.select_one('div.info-name h1').text if soup.select_one('div.info-name h1') else '',
                '状态': soup.select_one('div.info-label span').text if soup.select_one('div.info-label span') else '',
                '作者': soup.select_one('span.author-name-text').text if soup.select_one(
                    'span.author-name-text') else '',
                '章节数': chapter_count,
                '榜单': '女频新书榜',
                '类型': CATEGORY_MAPPING[category_id]
            }

            processed_novels.append(processed_novel)
            print(f"已获取《{processed_novel['书名']}》的信息")
            # time.sleep(1)

        return processed_novels

    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None


def main():
    connection = connect_to_database()
    if not connection:
        print("无法连接到数据库，程序退出")
        return

    try:
        # 遍历所有类型
        for category_id in CATEGORY_MAPPING.keys():
            print(f"\n开始爬取 {CATEGORY_MAPPING[category_id]} 类型的小说...")
            all_novels = []

            # 每个类型爬取3页
            for page in range(3, 4):
                novels = get_novel_list(page, category_id)
                if novels:
                    all_novels.extend(novels)
                    print(f"{CATEGORY_MAPPING[category_id]} 类型第{page}页数据获取完成")
                    # if page < 3:
                        # time.sleep(2)
                else:
                    print(f"{CATEGORY_MAPPING[category_id]} 类型第{page}页数据获取失败")
                    break

            if all_novels:
                save_to_database(all_novels, connection)
                print(f"\n{CATEGORY_MAPPING[category_id]} 类型共处理了 {len(all_novels)} 本小说的信息")

            # 每个类型之间暂停5秒，避免请求过于频繁
            # time.sleep(5)

    finally:
        connection.close()
        print("数据库连接已关闭")


if __name__ == "__main__":
    main()