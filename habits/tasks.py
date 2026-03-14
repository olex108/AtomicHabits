import os
import requests
from celery import shared_task
from .models import Habit


@shared_task
def send_telegram_reminder(habit_id):
    """
    Задача для отправки сообщения в Telegram.
    Принимает ID привычки, находит пользователя и его chat_id.
    """

    try:
        habit = Habit.objects.get(pk=habit_id)
        user = habit.user

        if not user.tg_chat_id:
            return f"У пользователя {user.phone} не привязан Telegram"

        message = (
            f"🔔 Напоминание о привычке!\n"
            f"Действие: {habit.action}\n"
            f"Место: {habit.place}\n"
            f"Время: {habit.time.strftime('%H:%M')}"
        )

        url = f"https://api.telegram.org{settings.TELEGRAM_BOT_API_KEY}/sendMessage"
        response = requests.post(url, data={
            "chat_id": user.tg_chat_id,
            "text": message
        })

        return response.json()

    except Habit.DoesNotExist:
        return f"Привычка с ID {habit_id} не найдена"