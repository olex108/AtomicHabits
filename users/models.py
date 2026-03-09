from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Model of user representing with field email for authentication of user

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

    Added fields for project
    email: email address of user is uniq field
    phone: phone number in formate "+XXXXXXXXXXX"
    country: country in charfield formate
    avatar: image of useer
    token: token to verification of user email
    """

    username = None
    email = models.EmailField(verbose_name="Почта", null=True, blank=True)
    phone = models.CharField(unique=True, max_length=15, verbose_name="Телефон")
    country = models.CharField(max_length=32, verbose_name="Страна", help_text="страна", blank=True, null=True)
    avatar = models.ImageField(
        upload_to="users/avatar/", verbose_name="Аватар", help_text="Загрузите аватар", blank=True, null=True
    )

    token = models.CharField(max_length=100, verbose_name="Token", blank=True, null=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
