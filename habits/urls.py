from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HabitViewSet

# Создаем роутер и регистрируем ViewSet
router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habits')

urlpatterns = [
    # Все стандартные CRUD методы будут доступны по адресу /habits/
    # Метод public_list будет доступен по адресу /habits/public/
    path('', include(router.urls)),
]