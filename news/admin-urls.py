from django.urls import path
from news import views as news
from auth_site import views as auth
from PBL6_Fake_News_Detection_BE.middleware import AdminAuthorizationMiddleware, UserAuthorizationMiddleware

app_name = 'Admin'

urlpatterns = [
   
    path('news_list/<int:number>/<int:page>', AdminAuthorizationMiddleware(news.news_list_admin), name='news_list_admin'),
    path('news_list_by_category/<int:category_id>/<int:number>/<int:page>', AdminAuthorizationMiddleware(news.news_list_by_category_admin), name='news_list_by_category_admin'),
    path('news_list_by_author/<int:author_id>/<int:number>/<int:page>', AdminAuthorizationMiddleware(news.news_list_by_author_admin), name='news_list_by_author_admin'),
    path('coments_list_by_user/<int:user_id>/<int:number>/<int:page>', AdminAuthorizationMiddleware(news.comments_list_by_user), name='coments_list_by_user'),
    path('list-admin/', AdminAuthorizationMiddleware(auth.admin_account_list), name='admin_account_list'),
    path('list-user/<int:number>/<int:page>', AdminAuthorizationMiddleware(auth.user_account_list), name='user_account_list'),
    path('change_user_account_permissions/<int:user_id>/', auth.change_user_account_permissions, name='change_user_account_permissions'),
    #thong ke admin
    path('total_news/<int:current_year>', news.total_news, name='total_news'),
    path('total_comments/<int:current_year>', news.total_comments, name='total_comments'),
    path('total/', news.total, name='total'),
    path('total_month/', news.total_month, name='total_month'),
    path('total_category/', news.total_category, name='total_category'),

    #all admin and user
    path('detail-user/<int:user_id>/', auth.user_detail, name='user_detail'),
    path('categories_list/', news.categories_list, name='categories_list'),
    path('detail-news/<int:news_id>/', news.news_detail, name='news_detail'),
    path('comments_list_by_news/<int:news_id>/<int:page>', news.comments_list_by_news, name='comments_list_by_news'),
    path('news/delete/<int:news_id>/', news.delete_news, name='delete_news'),
    path('update_profile/', auth.update_profile, name='update_profile'),
]                       