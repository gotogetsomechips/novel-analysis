# urls.py
from django.urls import path
from my_app import views

urlpatterns = [
    path('', views.novel_list, name='novel_list'),  # 首页
    path('list/<str:list_name>/', views.novel_list, name='novel_list_by_list'),  # 根据list过滤
    path('list/<str:list_name>/type/<str:type_name>/', views.novel_list, name='novel_list_by_list_and_type'),  # 根据list和type过滤
    path('novel-type-statistics/', views.novel_type_statistics, name='novel_type_statistics'),
    path('novel-type-statistics/', views.novel_type_statistics, name='novel_type_statistics'),
    path('novel-people-statistics/', views.novel_people_statistics, name='novel_people_statistics'),
    path('novel-chapter-statistics/', views.novel_chapter_statistics, name='novel_chapter_statistics'),
    path('recommended/', views.get_recommended_novels_by_type, name='recommended_novels'),
    path('recommended/<str:type_name>/', views.get_recommended_novels_by_type, name='recommended_novels_by_type'),
]