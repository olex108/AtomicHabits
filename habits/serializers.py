from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('user',) # Пользователь подставляется автоматически

    def validate(self, data):
        """Реализация логики clean() для API"""
        is_pleasant = data.get('is_pleasant_habit')
        related = data.get('related_habit')
        reward = data.get('reward')

        if is_pleasant and (related or reward):
            raise serializers.ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )
        if reward and related:
            raise serializers.ValidationError(
                "Нельзя одновременно выбрать вознаграждение и связанную привычку."
            )
        if related and not related.is_pleasant_habit:
            raise serializers.ValidationError(
                "Связанная привычка должна быть приятной."
            )
        return data