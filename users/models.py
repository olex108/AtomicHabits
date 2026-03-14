from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    """
    Model of user representing with field phone for authentication of user

    Field  from AbstractUser model
    id: id of user
    password: password
    last_login:
    is_superuser:
    first_name:
    last_name:
    is_staff:
    is_active:
    date_joined:

    phone: phone number in formate "+XXXXXXXXXXX"
    tg_chat_id: id of telegram bot. Get with first message to bot
    bot_token: field to verification and bind of bot
    """

    username = None
    phone = models.CharField(
        unique=True,
        max_length=15,
        verbose_name="Телефон",
        help_text="Введите номер в формате +79XXXXXXXXX"
    )
    tg_chat_id = models.CharField(
        max_length=50,
        verbose_name="Telegram Chat ID",
        blank=True,
        null=True,
        unique=True
    )

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone

    def set_bot_token(self):
        """Генерирует уникальный токен для привязки бота"""
        self.bot_token = str(uuid.uuid4())[:8]  # Короткий код из 8 символов
        self.save()

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
