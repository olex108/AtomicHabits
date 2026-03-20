import json

from django_celery_beat.models import CrontabSchedule, PeriodicTask


def create_periodic_task(habit):
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=habit.time.minute,
        hour=habit.time.hour,
        day_of_month=f"*/{habit.periodicity}",
    )

    PeriodicTask.objects.update_or_create(
        name=f"Habit reminder {habit.id}",
        defaults={
            "crontab": schedule,
            "task": "habits.tasks.send_telegram_reminder",
            "args": json.dumps([habit.id]),
        },
    )
