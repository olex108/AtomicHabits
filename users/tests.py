from users.models import User

from django.urls import reverse
from rest_framework import status
from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model


class UserModelTest(TestCase):
    def setUp(self):
        self.phone = "+79001112233"
        self.password = "testpass123"
        # Создаем пользователя для проверки __str__
        self.user = User.objects.create(phone=self.phone)
        self.user.set_password(self.password)
        self.user.save()

    def test_user_str(self):
        """Тестируем __str__"""
        self.assertEqual(str(self.user), self.phone)


class UserTestCase(APITestCase):

    def setUp(self):
        """Подготовка данных для тестов"""
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:token_obtain_pair')
        self.tg_id_url = reverse('users:set_telegram_id')
        self.user_data = {
            "phone": "+79001112233",
            "password": "testpassword123"
        }

    def test_user_registration(self):
        """Тест успешной регистрации"""
        response = self.client.post(self.register_url, self.user_data)

        # Проверяем статус 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Проверяем, что пользователь создался в БД
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().phone, self.user_data['phone'])
        # Проверяем, что пароль не вернулся в ответе
        self.assertNotIn('password', response.data)
        # Проверяем __str__ пользователя
        self.assertEqual(str(User.objects.get().phone), self.user_data['phone'])

    def test_user_login(self):
        """Тест получения JWT-токена"""
        # Регистрируем пользователя
        self.client.post(self.register_url, self.user_data)

        response = self.client.post(self.login_url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем наличие access и refresh токенов
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_registration_with_existing_phone(self):
        """Тест: нельзя зарегистрироваться с тем же телефоном дважды"""
        self.client.post(self.register_url, self.user_data)

        response = self.client.post(self.register_url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data)

    def test_login_wrong_credentials(self):
        """Тест: ошибка при неверном пароле"""
        self.client.post(self.register_url, self.user_data)

        bad_data = {
            "phone": self.user_data['phone'],
            "password": "wrong_password"
        }
        response = self.client.post(self.login_url, bad_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class TelegramIdUpdateTest(APITestCase):

    def setUp(self):
        # Создаем двух пользователей для проверки изоляции данных
        self.set_tg_url = reverse('users:set_telegram_id')
        self.register_url = reverse('users:register')

        self.user_data = {
            "phone": "+79001112233",
            "password": "testpassword123"
        }
        self.user_er_data = {
            "phone": "+79012345678",
            "password": "testpassword123"
        }

    def test_registration_and_set_telegram(self):
        """Тест: регистрация пользователя и последующее добавление Telegram ID"""

        # 1. Регистрация
        self.client.post(self.register_url, self.user_data)
        user = User.objects.get(phone=self.user_data["phone"])
        self.client.force_authenticate(user=user)

        # 2. Валидация: Ошибка при передаче букв
        bad_data = {"tg_chat_id": "id12345abc"}
        response_bad = self.client.patch(self.set_tg_url, bad_data)

        self.assertEqual(response_bad.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("tg_chat_id", response_bad.data)
        self.assertEqual(
            response_bad.data["tg_chat_id"][0],
            "Telegram Chat ID должен состоять только из цифр."
        )

        # 3. Успешная привязка корректного ID
        good_data = {"tg_chat_id": "987654321"}
        response_ok = self.client.patch(self.set_tg_url, good_data)

        self.assertEqual(response_ok.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.tg_chat_id, "987654321")

        # 4. Валидация: Ошибка уникальности
        self.client.post(self.register_url, self.user_er_data)
        other_user = User.objects.get(phone=self.user_er_data["phone"])

        self.client.force_authenticate(user=other_user)

        response_duplicate = self.client.patch(self.set_tg_url, good_data)
        self.assertEqual(response_duplicate.status_code, status.HTTP_400_BAD_REQUEST)
