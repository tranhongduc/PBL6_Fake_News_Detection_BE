from django.urls import path
from news import views as news
from auth_site import views as auth
from PBL6_Fake_News_Detection_BE.middleware import AdminAuthorizationMiddleware, UserAuthorizationMiddleware

app_name = 'Admin'

urlpatterns = [
   
    path('news_list/', AdminAuthorizationMiddleware(news.news_list_admin), name='news_list_admin'),
    path('news_list_by_category/<int:category_id>/', AdminAuthorizationMiddleware(news.news_list_by_category_admin), name='news_list_by_category_admin'),
    path('news_list_by_author/<int:author_id>/', AdminAuthorizationMiddleware(news.news_list_by_author_admin), name='news_list_by_author_admin'),
    path('coments_list_by_user/<int:user_id>/', AdminAuthorizationMiddleware(news.comments_list_by_user), name='coments_list_by_user'),
    path('list-admin/', AdminAuthorizationMiddleware(auth.admin_account_list), name='admin_account_list'),
    path('list-user/', AdminAuthorizationMiddleware(auth.user_account_list), name='user_account_list'),
    path('news/total/', news.total_news, name='total_news'),
    #all admin and user
    path('detail-user/<int:user_id>/', auth.user_detail, name='user_detail'),
    path('categories_list/', news.categories_list, name='categories_list'),
    path('detail-news/<int:news_id>/', news.news_detail, name='news_detail'),
    path('comments_list_by_news/<int:news_id>/<int:page>', news.comments_list_by_news, name='comments_list_by_news'),
    path('news/delete/<int:news_id>/', news.delete_news, name='delete_news'),
    path('update_profile/', auth.update_profile, name='update_profile'),
]                       