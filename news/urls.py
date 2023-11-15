from django.urls import path
from news import views
from PBL6_Fake_News_Detection_BE.middleware import AdminAuthorizationMiddleware, UserAuthorizationMiddleware

urlpatterns = [
    path('admin/categories_list/', AdminAuthorizationMiddleware(views.categories_list), name='admin_categories_list'),
    path('admin/news_list/', AdminAuthorizationMiddleware(views.news_list), name='news_list'),
    path('admin/news_list_by_category/<int:category_id>/', AdminAuthorizationMiddleware(views.news_list_by_category), name='news_list_by_category'),
    path('admin/news_list_by_author/<int:author_id>/', AdminAuthorizationMiddleware(views.news_list_by_author), name='news_list_by_author'),
    path('admin/coments_list_by_user/<int:user_id>/', AdminAuthorizationMiddleware(views.coments_list_by_user), name='coments_list_by_user'),
    path('admin/detail-news/<int:id>/', AdminAuthorizationMiddleware(views.news_detail), name='news_detail'),

    path('user/categories/', views.get_all_categories, name='get_all_categories'),
    path('user/news/', UserAuthorizationMiddleware(views.get_all_news), name='get_all_news'),
    path('user/comments/', UserAuthorizationMiddleware(views.get_all_comments), name='get_all_comments'),
    path('user/news/total/', views.total_news, name='total_news'),
    path('user/paging/', views.paging, name='paging'),
    path('user/news/<int:id>/', views.get_news_detail, name='get_news_detail'),
]                       