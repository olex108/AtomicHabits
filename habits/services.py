import json
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.conf import settings

def create_periodic_task(habit):
    # 1. Создаем или получаем расписание
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=habit.time.minute,
        hour=habit.time.hour,
        day_of_month=f'*/{habit.periodicity}',
        # Если в settings.py указано USE_TZ = True,
        # убедитесь, что CELERY_TIMEZONE настроен верно
    )

    # 2. Используем update_or_create, чтобы не было ошибки при редактировании привычки
    PeriodicTask.objects.update_or_create(
        name=f'Habit reminder {habit.id}', # Уникальный ключ для поиска
        defaults={
            'crontab': schedule,
            'task': 'habits.tasks.send_telegram_reminder',
            'args': json.dumps([habit.id]),
        }
    )
