from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserRegistrationView, UserProfileView, 
    UserView, PasswordChangeView, UserListView
)

urlpatterns = [
    # Authentication URLs
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User Management URLs
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('me/', UserView.as_view(), name='me'),
    path('change-password/', PasswordChangeView.as_view(), name='change_password'),
    path('users/', UserListView.as_view(), name='user_list'),
]