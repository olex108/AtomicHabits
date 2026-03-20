from rest_framework import serializers

from .models import Habit
from .validators import (CompleteTimeValidator, PeriodicityValidator, PleasantHabitLogicValidator,
                         RelatedHabitIsPleasantValidator, RewardOrRelatedHabitValidator)


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("user",)
        validators = [
            RewardOrRelatedHabitValidator(),
            CompleteTimeValidator(),
            RelatedHabitIsPleasantValidator(),
            PleasantHabitLogicValidator(),
            PeriodicityValidator(),
        ]
