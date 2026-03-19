from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    # Поле пароля только для записи (не будет отображаться в GET запросах)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "phone", "password", "tg_chat_id")

    def create(self, validated_data):
        # 1. Извлекаем пароль из данных
        password = validated_data.pop('password')

        # 2. Создаем объект пользователя БЕЗ пароля и БЕЗ вызова create_user
        user = User.objects.create(**validated_data)

        # 3. Хешируем и сохраняем пароль вручную
        user.set_password(password)
        user.save()

        return user


class TelegramIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("tg_chat_id",)

    def validate_tg_chat_id(self, value):
        """Проверка, что ID состоит только из цифр"""
        if value and not value.isdigit():
            raise serializers.ValidationError("Telegram Chat ID должен состоять только из цифр.")
        return value
