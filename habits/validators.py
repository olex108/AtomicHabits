from datetime import time
from django.core.exceptions import ValidationError


def validate_duration(value):
    # Условие: время не должно превышать 2 минуты (120 секунд)
    if value > time(hour=0, minute=2, second=0):
        raise ValidationError("Время выполнения не может быть больше 120 секунд.")
