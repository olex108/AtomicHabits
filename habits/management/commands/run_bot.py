import os
import time
import requests
from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = 'Запуск бота через Long Polling на чистом requests'

    def handle(self, *args, **options):
        token = os.getenv('BOT_API_KEY')
        base_url = f"https://api.telegram.org/bot{token}/"
        offset = 0

        self.stdout.write(self.style.SUCCESS('Бот запущен (без сторонних библиотек)...'))

        while True:
            try:
                # Получаем обновления
                response = requests.get(f"{base_url}getUpdates", params={'offset': offset, 'timeout': 30})
                updates = response.json().get('result', [])

                for update in updates:
                    offset = update['update_id'] + 1
                    message = update.get('message', {})
                    chat_id = message.get('chat', {}).get('id')

                    # 1. Если пришла команда /start
                    if 'text' in message and message['text'] == '/start':
                        self.send_contact_request(base_url, chat_id)

                    # 2. Если пришел контакт
                    if 'contact' in message:
                        contact = message['contact']
                        phone = contact['phone_number'].replace('+', '')

                        user = User.objects.filter(phone__contains=phone).first()
                        if user:
                            user.tg_chat_id = str(chat_id)
                            user.save()
                            requests.post(f"{base_url}sendMessage", data={
                                'chat_id': chat_id,
                                'text': f"Аккаунт {user.phone} привязан! ID: {chat_id}"
                            })
                        else:
                            requests.post(f"{base_url}sendMessage", data={
                                'chat_id': chat_id,
                                'text': "Номер не найден в базе Django."
                            })

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
                time.sleep(5)

    def send_contact_request(self, url, chat_id):
        reply_markup = {
            "keyboard": [[{"text": "Отправить контакт", "request_contact": True}]],
            "one_time_keyboard": True,
            "resize_keyboard": True
        }
        requests.post(f"{url}sendMessage", json={
            'chat_id': chat_id,
            'text': "Нажмите кнопку ниже, чтобы подтвердить номер телефона:",
            'reply_markup': reply_markup
        })
