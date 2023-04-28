import os
from dotenv import load_dotenv
from telegram_bot.chat_gpt_bot import ChatGptBot

load_dotenv()

OPENAI_ORG = os.getenv('OPENAI_ORG')
OPENAI_KEY = os.getenv('OPENAI_KEY')
ELEVENLABS_KEY = os.getenv('ELEVENLABS_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

if __name__ == '__main__':
    chat_gpt_bot = ChatGptBot(TELEGRAM_TOKEN, OPENAI_ORG, OPENAI_KEY, ELEVENLABS_KEY)
    chat_gpt_bot.start_bot()