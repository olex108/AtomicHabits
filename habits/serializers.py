from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('user',) # Пользователь подставляется автоматически

    def validate(self, data):
        """
        Комплексная валидация всех бизнес-правил
        """
        # Получаем значения из входящих данных (учитывая частичное обновление patch)
        is_pleasant = data.get('is_pleasant_habit', getattr(self.instance, 'is_pleasant_habit', False))
        related_habit = data.get('related_habit', getattr(self.instance, 'related_habit', None))
        reward = data.get('reward', getattr(self.instance, 'reward', None))
        complete_time = data.get('complete_time', getattr(self.instance, 'complete_time', None))
        periodicity = data.get('periodicity', getattr(self.instance, 'periodicity', None))

        # 1. Исключить одновременный выбор связанной привычки и вознаграждения
        if related_habit and reward:
            raise serializers.ValidationError(
                "Нельзя одновременно заполнить поле вознаграждения и связанной привычки."
            )

        # 2. Время выполнения должно быть не больше 120 секунд
        if complete_time and complete_time > timedelta(seconds=120):
            raise serializers.ValidationError(
                "Время выполнения должно быть не больше 120 секунд."
            )

        # 3. В связанные привычки могут попадать только приятные привычки
        if related_habit and not related_habit.is_pleasant_habit:
            raise serializers.ValidationError(
                "В связанные привычки можно добавлять только привычки с признаком приятной."
            )

        # 4. У приятной привычки не может быть вознаграждения или связанной привычки
        if is_pleasant:
            if reward or related_habit:
                raise serializers.ValidationError(
                    "У приятной привычки не может быть вознаграждения или связанной привычки."
                )

        # 5. Периодичность (не реже 1 раза в 7 дней)
        if periodicity:
            if periodicity > 7:
                raise serializers.ValidationError(
                    "Нельзя выполнять привычку реже, чем 1 раз в 7 дней."
                )
            if periodicity < 1:
                raise serializers.ValidationError(
                    "Периодичность не может быть меньше 1 дня."
                )

        return data