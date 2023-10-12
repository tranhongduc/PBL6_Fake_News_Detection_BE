from django.urls import path
from news import views

urlpatterns = [
    path("categories_list/", views.categories_list, name="categories_list"),
    path("news_list/", views.news_list, name="news_list"),
    path('news_list_by_category/<int:category_id>/', views.news_list_by_category, name='news_list_by_category'),
    path('news_list_by_author/<int:author_id>/', views.news_list_by_author, name='news_list_by_author'),
    path('coments_list_by_user/<int:user_id>/', views.coments_list_by_user, name='coments_list_by_user'),
    path('detail-news/<int:id>/', views.news_detail, name='news_detail'),
]