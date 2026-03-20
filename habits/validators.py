from datetime import timedelta

from rest_framework import serializers


class RewardOrRelatedHabitValidator:
    """Исключает одновременный выбор связанной привычки и вознаграждения"""

    def __call__(self, data):
        reward = data.get("reward")
        related_habit = data.get("related_habit")
        if reward and related_habit:
            raise serializers.ValidationError(
                "Нельзя одновременно заполнить поле вознаграждения и связанной привычки."
            )


class CompleteTimeValidator:
    """Время выполнения должно быть не больше 120 секунд"""

    def __call__(self, data):
        complete_time = data.get("complete_time")
        if complete_time and complete_time > timedelta(seconds=120):
            raise serializers.ValidationError("Время выполнения должно быть не больше 120 секунд.")


class RelatedHabitIsPleasantValidator:
    """В связанные привычки могут попадать только приятные привычки"""

    def __call__(self, data):
        related_habit = data.get("related_habit")
        if related_habit and not related_habit.is_pleasant_habit:
            raise serializers.ValidationError("В связанные привычки можно добавлять только приятные привычки.")


class PleasantHabitLogicValidator:
    """У приятной привычки не может быть вознаграждения или связанной привычки"""

    def __call__(self, data):
        is_pleasant = data.get("is_pleasant_habit")
        reward = data.get("reward")
        related_habit = data.get("related_habit")
        if is_pleasant and (reward or related_habit):
            raise serializers.ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )


class PeriodicityValidator:
    """Периодичность не реже 1 раза в 7 дней и не чаще 1 раза в 1 день"""

    def __call__(self, data):
        periodicity = data.get("periodicity")
        if periodicity:
            if periodicity > 7:
                raise serializers.ValidationError("Нельзя выполнять привычку реже 1 раза в 7 дней.")
            if periodicity < 1:
                raise serializers.ValidationError("Периодичность не может быть меньше 1 дня.")
