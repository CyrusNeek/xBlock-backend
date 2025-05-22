import telebot
import os

# Replace 'your-telegram-bot-token' with your bot's token
bot_token = os.getenv("TELEGRAM_BOT_API_KEY")
bot = telebot.TeleBot(token=bot_token)


def main():
    
    bot.send_message(
        chat_id=-4252955861,
        text = "This a test message from bot"
    )
    
    

if __name__ == "django.core.management.commands.shell":
    main()