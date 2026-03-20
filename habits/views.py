from rest_framework import generics, permissions, viewsets

from .models import Habit
from .pagination import HabitPaginator
from .permissions import IsOwner
from .serializers import HabitSerializer
from .services import create_periodic_task


class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с привычками пользователя
    """

    serializer_class = HabitSerializer
    pagination_class = HabitPaginator

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user).order_by("id")

    def perform_create(self, serializer):

        habit = serializer.save(user=self.request.user)
        # Если у пользователя привязан ТГ, создаем задачу
        if habit.user.tg_chat_id:
            create_periodic_task(habit)

    def get_permissions(self):
        # Для действий с объектом проверяем владельца
        if self.action in ["update", "partial_update", "destroy", "retrieve"]:
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]


class PublicHabitListAPIView(generics.ListAPIView):
    """
    Эндпоинт для просмотра ВСЕХ публичных привычек всех пользователей.
    """

    serializer_class = HabitSerializer
    queryset = Habit.objects.filter(is_public=True).order_by("id")
    pagination_class = HabitPaginator
    permission_classes = [permissions.IsAuthenticated]
