from django.urls import path
from news import views as news
from auth_site import views as auth

from PBL6_Fake_News_Detection_BE.middleware import AdminAuthorizationMiddleware, UserAuthorizationMiddleware

app_name = 'user'
urlpatterns = [
    # all user see and search news
    path('list_news_user/<int:number>/<int:page>', news.news_list_user, name='news_list_user'),
    path('search/<int:number>/<int:page>/', news.search_news, name='search_news'),
    # account user or user view other users' accounts
    path('list_new_real_by_author/<int:author_id>/<int:number>/<int:page>', news.list_news_real_by_author, name='list_news_real_by_author'),
    path('search_real_in_user/<int:author_id>/<int:number>/<int:page>/', news.search_news_real_by_author, name='search_news_real_by_author'),
    # Only accounts can view it
    path('list_new_fake_by_author/<int:number>/<int:page>', news.list_news_fake_by_author, name='list_news_fake_by_author'), 
    path('search_fake_in_user/<int:number>/<int:page>/', news.search_news_fake_by_author, name='search_news_fake_by_author'),
    
    path('list_user_you_follow/<int:page>', auth.list_user_you_follow, name='list_user_you_follow'),
    path('list_user_following_you/<int:page>', auth.list_user_you_follow, name='list_user_you_follow'),
    
    path('news/store/', news.store_news, name='store_news'),
    path('news/update/<int:news_id>/', news.update_news, name='update_news'),
    path('comment/store/', news.store_comment, name='store_comment'),
    path('comment/update/<int:comment_id>/', news.update_comment, name='update_comment'),
]

 
                 