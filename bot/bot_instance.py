from aiogram import Bot
from os import getenv
from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("API_KEY")

bot = Bot(token=TOKEN)