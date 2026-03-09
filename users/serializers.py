import os
import secrets

from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import serializers

from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    User registration serializer with fields of User model. Add password1 and password2 fields to confirm password
    """

    password1 = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["email", "password1", "password2", "phone", "country", "avatar"]

    def create(self, validated_data: dict) -> User:
        """
        Creates a new user
        Check that password1 and password2 match
        Create new user with fields and set password
        Create and add token
        Get url of email confirm and send email for user

        :param validated_data: dict
        :return: user
        """

        if validated_data["password1"] != validated_data["password2"]:
            raise serializers.ValidationError("Пароль должен совпадать")

        user = User.objects.create(
            email=validated_data["email"],
            phone=validated_data["phone"],
            country=validated_data["country"],
            avatar=validated_data["avatar"],
            is_active=False,
            last_login=timezone.now(),
        )
        user.set_password(validated_data["password1"])
        token = secrets.token_hex(16)
        user.token = token
        user.save()

        request = self.context.get("request")

        if request:
            host = request.get_host()
            url = f"http://{host}/users/email_confirm/{token}/"

            try:
                send_mail(
                    subject="Добро пожаловать в нашу онлайн школу",
                    message=f"""Спасибо что зарегистрировались в нашем сервисе! 
                    Перейдите по ссылке для подтверждения почты {url}.
                    """,
                    from_email=os.getenv("EMAIL_ADDRESS"),
                    recipient_list=[user.email],
                )

            except Exception as e:
                print("Error:", e)

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "phone", "country", "avatar"]


class UserRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone", "country", "avatar"]
