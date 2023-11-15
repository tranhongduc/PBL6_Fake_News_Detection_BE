from django.urls import path
from auth_site import views
from .views import MyTokenObtainPairView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("get-user-info/", views.get_user_info, name="get_user_info"),
    path('refresh-token/', views.refresh_token, name='refresh_token'),
    path('list-admin/', views.admin_account_list, name='admin_account_list'),
    path('list-user/', views.user_account_list, name='user_account_list'),
    path('detail-user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]