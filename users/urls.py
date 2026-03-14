from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from . import views
from .apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    # 1. Регистрация
    path('register/', views.UserCreateAPIView.as_view(), name='user-register'),
    # 2. Авторизация (получение JWT токена по телефону и паролю)
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # 3. Обновление токена
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]