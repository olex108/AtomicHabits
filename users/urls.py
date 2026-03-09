from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views
from .apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path("register/", views.UserRegisterAPIView.as_view(), name="register"),
    path("users/email_confirm/<str:token>/", views.UserEmailVerificationAPIView.as_view(), name="email-confirm"),
    path("users/<int:pk>/", views.UserRetrieveAPIView.as_view(), name="user-get"),
    path("users/<int:pk>/update/", views.UserUpdateAPIView.as_view(), name="user-update"),
    path("users/<int:pk>/delete/", views.UserDestroyAPIView.as_view(), name="user-delete"),
    # token
    path("login/", views.LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]