from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .apps import HabitsConfig
from .views import HabitViewSet, PublicHabitListAPIView

app_name = HabitsConfig.name

router = DefaultRouter()
router.register(r"habits", HabitViewSet, basename="habits")

urlpatterns = [
    path("public_habits/", PublicHabitListAPIView.as_view(), name="public_habits"),
    path("", include(router.urls)),
]
