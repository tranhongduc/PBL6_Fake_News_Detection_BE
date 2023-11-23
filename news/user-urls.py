from django.urls import path
from news import views as news
from auth_site import views as auth

from PBL6_Fake_News_Detection_BE.middleware import AdminAuthorizationMiddleware, UserAuthorizationMiddleware

app_name = 'user'
urlpatterns = [
    path('categories/', news.get_all_categories, name='get_all_categories'),
    path('news/', UserAuthorizationMiddleware(news.get_all_news), name='get_all_news'),
    path('comments/', UserAuthorizationMiddleware(news.get_all_comments), name='get_all_comments'),
    path('news/total/', news.total_news, name='total_news'),
    path('paging/', news.paging, name='paging'),
    path('news/<int:id>/', news.get_news_detail, name='get_news_detail'),
    path('list_user_you_follow/<int:user_id>/<int:page>', auth.list_user_you_follow, name='list_user_you_follow'),
    path('list_user_following_you/<int:user_id>/<int:page>', auth.list_user_you_follow, name='list_user_you_follow'),
    path('news/store/', news.store_news, name='store_news'),
    path('news/update/<int:news_id>/', news.update_news, name='update_news'),
]                       