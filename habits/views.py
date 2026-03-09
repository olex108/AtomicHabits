from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Habit
from .serializers import HabitSerializer
from .pagination import HabitPaginator # Если нужна кастомная пагинация
from .permissions import IsOwner


class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    pagination_class = HabitPaginator

    def get_permissions(self):
        """
        Метод гибкой настройки прав для разных действий.
        """
        if self.action in ['update', 'partial_update', 'destroy', 'retrieve']:
            # Редактировать, удалять и смотреть детали может только владелец
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        else:
            # Создавать и смотреть списки может любой авторизованный юзер
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Фильтрация:
        - В обычном списке — только свои.
        - В списке 'public' — только публичные.
        """

        if self.action == 'public_list':
            return Habit.objects.filter(is_public=True)
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='public')
    def public_list(self, request):
        """Эндпоинт: Список публичных привычек"""

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)