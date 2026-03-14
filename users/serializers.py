from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    # Поле пароля только для записи (не будет отображаться в GET запросах)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "phone", "password", "tg_chat_id")

    def create(self, validated_data):
        """
        Метод create_user автоматически хеширует пароль
        и сохраняет пользователя в базу данных.
        """
        return User.objects.create_user(**validated_data)
