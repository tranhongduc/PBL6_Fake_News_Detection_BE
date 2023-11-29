from django.urls import path
from news import views as news
from auth_site import views as auth

from PBL6_Fake_News_Detection_BE.middleware import AdminAuthorizationMiddleware, UserAuthorizationMiddleware

app_name = 'user'
urlpatterns = [
    path('paging/', news.paging, name='paging'),
    path('list_user_you_follow/<int:user_id>/<int:page>', auth.list_user_you_follow, name='list_user_you_follow'),
    path('list_user_following_you/<int:user_id>/<int:page>', auth.list_user_you_follow, name='list_user_you_follow'),
    path('list_news_user/<int:number>/<int:page>', news.news_list_user, name='news_list_user'),
    path('news/store/', news.store_news, name='store_news'),
    path('news/update/<int:news_id>/', news.update_news, name='update_news'),
    path('comment/store/', news.store_comment, name='store_comment'),
    path('comment/update/<int:comment_id>/', news.update_comment, name='update_comment'),
    path('news_list_by_author_user_real/<int:author_id>/<int:number>/<int:page>', news.news_list_by_author_user_real, name='news_list_by_author_user_real'),
    path('news_list_by_author_user_fake/', news.news_list_by_author_user_fake, name='news_list_by_author_user_fake'),
    path('search/<int:number>/<int:page>/', news.search_news, name='search_news'),
]                       