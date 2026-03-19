from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import User
from .serializers import UserSerializer, TelegramIdSerializer


class UserCreateAPIView(generics.CreateAPIView):
    """Эндпоинт для регистрации нового пользователя"""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]


class TelegramUpdateAPIView(generics.UpdateAPIView):
    """
    Эндпоинт для привязки Telegram Chat ID к профилю текущего пользователя.
    """
    serializer_class = TelegramIdSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Возвращает объект текущего авторизованного пользователя
        return self.request.user