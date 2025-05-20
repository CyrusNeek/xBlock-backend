import traceback
from django.conf import settings
import telebot
import logging


logging.getLogger(__name__)


class TelegramBotMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.bot = telebot.TeleBot(token=settings.TELEGRAM_BOT_API_KEY)

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 500:
            self.send_error_message(request)
        return response

    def send_error_message(self, request):
        error_message = traceback.format_exc()
        message = f"Error 500\n\nURL: {request.build_absolute_uri()}\n\n{error_message}"
        try:
            self.bot.send_message(chat_id=settings.TELEGRAM_BOT_GROUP_ID, text=message)
        except Exception as e:
            print(f"Failed to send message to Telegram: {e}")
