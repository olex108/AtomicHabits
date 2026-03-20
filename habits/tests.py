import sys
from datetime import time, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

import config.asgi  # noqa: F401
import config.wsgi  # noqa: F401
import manage
from config.celery import app as celery_app  # noqa: F401
from habits.validators import CompleteTimeValidator, PeriodicityValidator, RelatedHabitIsPleasantValidator
from users.models import User

from .models import Habit
from .views import HabitViewSet, PublicHabitListAPIView

from unittest.mock import MagicMock

from habits.tasks import send_telegram_reminder


class HabitTestCase(APITestCase):

    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        # Создаем пользователей
        self.user = User.objects.create(phone="+79001112233")
        self.user.set_password("test_pass")
        self.user.save()

        self.other_user = User.objects.create(phone="+79998887766")
        self.other_user.set_password("other_pass")
        self.other_user.save()

        # Приятная привычка для тестов связей
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time=time(10, 0),
            action="Приятное действие",
            is_pleasant_habit=True,
            is_public=True,
        )

    def test_habit_str(self):
        """Покрытие метода __str__ в models.py"""
        self.assertEqual(str(self.pleasant_habit), "Приятное действие")

    def test_create_habit_success(self):
        """Успешное создание привычки владельцем"""
        view = HabitViewSet.as_view({"post": "create"})
        data = {
            "place": "Спортзал",
            "time": "18:00:00",
            "action": "Бег",
            "is_pleasant_habit": False,
            "periodicity": 1,
            "complete_time": "00:02:00",
            "is_public": True,
        }
        request = self.factory.post(reverse("habits:habits-list"), data, format="json")
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.filter(user=self.user).count(), 2)

    def test_create_habit_with_task(self):
        """Успешное создание привычки владельцем"""

        self.user.tg_chat_id = 1234
        self.user.save()

        view = HabitViewSet.as_view({"post": "create"})
        data = {
            "place": "Спортзал",
            "time": "18:00:00",
            "action": "Бег",
            "is_pleasant_habit": False,
            "periodicity": 1,
            "complete_time": "00:02:00",
            "is_public": True,
        }
        request = self.factory.post(reverse("habits:habits-list"), data, format="json")
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.filter(user=self.user).count(), 2)

    def test_public_habits_list(self):
        """Тест Generic View для публичных привычек"""
        Habit.objects.create(
            user=self.other_user,
            action="Йога",
            is_pleasant_habit=False,
            is_public=True,
            time=time(9, 0),
            place="Парк",
            periodicity=1,
        )

        view = PublicHabitListAPIView.as_view()
        request = self.factory.get(reverse("habits:public_habits"))
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_habit_update_is_owner(self):
        """Тест: редактирование своей привычки"""
        view = HabitViewSet.as_view({"patch": "partial_update"})
        request = self.factory.patch(
            reverse("habits:habits-detail", args=[self.pleasant_habit.id]), {"action": "Новое название"}, format="json"
        )
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.pleasant_habit.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pleasant_habit.refresh_from_db()
        self.assertEqual(self.pleasant_habit.action, "Новое название")

    def test_habit_delete_is_owner(self):
        """Тест: удаление своей привычки"""
        view = HabitViewSet.as_view({"delete": "destroy"})
        request = self.factory.delete(reverse("habits:habits-detail", args=[self.pleasant_habit.id]))
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.pleasant_habit.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(id=self.pleasant_habit.id).exists())

    def test_validator_pleasant_habit_logic(self):
        """Тест: у приятной привычки не может быть награды или связанной привычки"""
        view = HabitViewSet.as_view({"post": "create"})
        data = {
            "action": "Приятная с наградой",
            "place": "X",
            "time": "10:00:00",
            "is_pleasant_habit": True,
            "reward": "Шоколад",
            "is_public": False,  # Добавили обязательное поле
            "periodicity": 1,  # Добавили обязательное поле
        }
        request = self.factory.post("/habits/", data, format="json")
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Проверяем наличие ошибки от нашего валидатора
        self.assertIn("У приятной привычки не может быть вознаграждения", str(response.data))

    def test_validator_min_periodicity(self):
        """Тест: периодичность меньше 1 дня"""
        view = HabitViewSet.as_view({"post": "create"})
        data = {
            "action": "Часто",
            "place": "X",
            "time": "10:00:00",
            "is_pleasant_habit": False,
            "is_public": False,
            "periodicity": 0,  # Вызовет ошибку
        }
        request = self.factory.post("/habits/", data, format="json")
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Так как встроенный валидатор модели может сработать первым,
        # проверяем наличие системного сообщения, если кастомное не прошло
        self.assertTrue(
            "greater than or equal to 1" in str(response.data)
            or "Периодичность не может быть меньше 1 дня." in str(response.data)
        )

    def test_validator_max_periodicity(self):
        """Тест: периодичность больше 7 дней"""
        view = HabitViewSet.as_view({"post": "create"})
        data = {
            "action": "Редко",
            "place": "X",
            "time": "10:00:00",
            "is_pleasant_habit": False,
            "is_public": False,
            "periodicity": 8,
        }
        request = self.factory.post("/habits/", data, format="json")
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            "less than or equal to 7" in str(response.data) or "реже 1 раза в 7 дней" in str(response.data)
        )

    def test_validator_pleasant_habit_with_related(self):
        """Тест: у приятной привычки не может быть СВЯЗАННОЙ привычки (ветка if)"""
        # Создаем еще одну приятную привычку для связи
        other_pleasant = Habit.objects.create(
            user=self.user, action="Чай", is_pleasant_habit=True, time=time(1, 1), place="X", is_public=True
        )

        view = HabitViewSet.as_view({"post": "create"})
        data = {
            "action": "Приятная со связью",
            "place": "X",
            "time": "10:00:00",
            "is_pleasant_habit": True,
            "related_habit": other_pleasant.id,  # Ошибка здесь
            "is_public": False,
            "periodicity": 1,
        }
        request = self.factory.post("/habits/", data, format="json")
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validator_related_habit_is_not_pleasant(self):
        """Тест: в связанные привычки нельзя добавить НЕприятную привычку"""
        # 1. Создаем НЕприятную привычку прямо внутри теста для надежности
        not_pleasant = Habit.objects.create(
            user=self.user,
            action="Трудная работа",
            is_pleasant_habit=False,  # Обязательно False
            time=time(1, 1),
            place="Офис",
            periodicity=1,
            is_public=True,
        )

        view = HabitViewSet.as_view({"post": "create"})
        data = {
            "action": "Полезная привычка",
            "place": "Дом",
            "time": "10:00:00",
            "related_habit": not_pleasant.id,  # Пытаемся привязать НЕприятную
            "is_pleasant_habit": False,
            "is_public": False,
            "periodicity": 1,
        }

        request = self.factory.post("/habits/", data, format="json")
        force_authenticate(request, user=self.user)
        response = view(request)

        # 2. Проверяем статус и сообщение
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validator_periodicity_limits(self):
        """Тест: проверка обеих границ периодичности (0 и 8)"""
        view = HabitViewSet.as_view({"post": "create"})

        # Граница > 7
        data_high = {
            "action": "A",
            "place": "X",
            "time": "10:00:00",
            "periodicity": 8,
            "is_pleasant_habit": False,
            "is_public": False,
        }
        request_high = self.factory.post("/habits/", data_high, format="json")
        force_authenticate(request_high, user=self.user)
        self.assertEqual(view(request_high).status_code, status.HTTP_400_BAD_REQUEST)

        # Граница < 1
        data_low = {
            "action": "B",
            "place": "X",
            "time": "10:00:00",
            "periodicity": 0,
            "is_pleasant_habit": False,
            "is_public": False,
        }
        request_low = self.factory.post("/habits/", data_low, format="json")
        force_authenticate(request_low, user=self.user)
        self.assertEqual(view(request_low).status_code, status.HTTP_400_BAD_REQUEST)


class PureValidatorTest(TestCase):
    def setUp(self):
        # Создаем пользователя и привычку для тестов связей
        from users.models import User

        self.user = User.objects.create(phone="+71112223344")
        self.not_pleasant_habit = Habit.objects.create(
            user=self.user,
            action="Труд",
            is_pleasant_habit=False,
            time="10:00",
            place="X",
            periodicity=1,
            is_public=True,
        )

    def test_complete_time_validator_pure(self):
        validator = CompleteTimeValidator()
        # Данные, которые ДОЛЖНЫ вызвать ошибку
        data = {"complete_time": timedelta(seconds=121)}
        with self.assertRaises(ValidationError) as cm:
            validator(data)
        self.assertIn("не больше 120 секунд", str(cm.exception))

    def test_related_habit_is_pleasant_validator_pure(self):
        validator = RelatedHabitIsPleasantValidator()
        # Передаем НЕприятную привычку
        data = {"related_habit": self.not_pleasant_habit}
        with self.assertRaises(ValidationError) as cm:
            validator(data)
        self.assertIn("только приятные привычки", str(cm.exception))

    def test_periodicity_validator_pure(self):
        validator = PeriodicityValidator()

        # Тест на > 7
        with self.assertRaises(ValidationError):
            validator({"periodicity": 8})

        # Тест на < 1
        with self.assertRaises(ValidationError):
            validator({"periodicity": 0.1})

    def test_reward_or_related_habit_validator_pure(self):
        from habits.validators import RewardOrRelatedHabitValidator

        validator = RewardOrRelatedHabitValidator()

        # Данные, где заполнены ОБА поля (это должно вызвать ошибку)
        data = {"reward": "Шоколадка", "related_habit": self.not_pleasant_habit}  # Передаем объект или его ID

        # Проверяем, что выбрасывается ValidationError
        with self.assertRaises(ValidationError) as cm:
            validator(data)

        # Проверяем текст ошибки (по желанию, для точности)
        self.assertIn("Нельзя одновременно заполнить", str(cm.exception))


class TaskTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(phone="+71112223344", tg_chat_id="12345")
        self.habit = Habit.objects.create(
            user=self.user,
            action="Выпить воды",
            place="Кухня",
            time=time(10, 0),
            is_pleasant_habit=False,
            periodicity=1,
            is_public=True,
        )

    @patch("requests.post")
    def test_send_reminder_success(self, mock_post):
        """Тест: успешная отправка напоминания"""
        # Имитируем успешный ответ от Telegram
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True}
        mock_post.return_value = mock_response

        result = send_telegram_reminder(self.habit.id)

        self.assertEqual(result, {"ok": True})
        mock_post.assert_called_once()

    def test_send_reminder_no_chat_id(self):
        """Тест: у пользователя нет tg_chat_id"""
        self.user.tg_chat_id = None
        self.user.save()

        result = send_telegram_reminder(self.habit.id)
        self.assertIn("не привязан Telegram", result)

    def test_send_reminder_habit_not_found(self):
        """Тест: привычка не найдена (DoesNotExist)"""
        result = send_telegram_reminder(999)
        self.assertIn("не найдена", result)


class ManagePyTest(TestCase):
    def test_manage_main_execution(self):
        """Тест для полного покрытия manage.py"""
        # 1. Имитируем аргументы командной строки (например, вызов справки)
        with patch.object(sys, "argv", ["manage.py", "help"]):
            # 2. Подменяем реальное выполнение команды заглушкой
            with patch("django.core.management.execute_from_command_line") as mock_exec:
                # 3. Вызываем функцию main() напрямую
                manage.main()
                # Проверяем, что функция попыталась выполнить команду
                mock_exec.assert_called_once_with(["manage.py", "help"])

    def test_manage_import_error(self):
        """Тест ветки ImportError в manage.py (если она есть)"""
        with patch.object(sys, "argv", ["manage.py", "help"]):
            with patch("django.core.management.execute_from_command_line", side_effect=ImportError):
                with self.assertRaises(ImportError):
                    manage.main()
