from rest_framework import viewsets, generics, permissions
from .models import Habit
from .serializers import HabitSerializer
from .pagination import HabitPaginator
from .permissions import IsOwner

from .services import create_periodic_task


class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с ЛИЧНЫМИ привычками пользователя (CRUD).
    Здесь будут отображаться и публичные, и приватные привычки текущего юзера.
    """
    serializer_class = HabitSerializer
    pagination_class = HabitPaginator

    def get_queryset(self):
        # Пользователь видит только свои объекты (любого типа приватности)
        return Habit.objects.filter(user=self.request.user).order_by('id')

    def perform_create(self, serializer):
        # При создании автоматически назначаем владельца
        serializer.save(user=self.request.user)

        def perform_create(self, serializer):
            habit = serializer.save(user=self.request.user)
            # Если у пользователя привязан ТГ, создаем задачу
            if habit.user.tg_chat_id:
                create_periodic_task(habit)

    def get_permissions(self):
        # Для действий с конкретным объектом (id) проверяем владельца
        if self.action in ['update', 'partial_update', 'destroy', 'retrieve']:
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]


class PublicHabitListAPIView(generics.ListAPIView):
    """
    Эндпоинт для просмотра ВСЕХ публичных привычек всех пользователей.
    Доступен только для чтения (List).
    """
    serializer_class = HabitSerializer
    queryset = Habit.objects.filter(is_public=True).order_by('id')
    pagination_class = HabitPaginator
    permission_classes = [permissions.IsAuthenticated]