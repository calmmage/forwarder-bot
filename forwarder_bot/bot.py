import os

from aiogram import Bot, Dispatcher
from botspot.core.bot_manager import BotManager
from dotenv import load_dotenv

from forwarder_bot.app import App
from forwarder_bot.handler import router

load_dotenv()

app = App()

dp = Dispatcher()
dp.include_router(router)
dp["app"] = app

bot = Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])

bm = BotManager(
    bot=bot,
    error_handler={"enabled": True},
)
bm.setup_dispatcher(dp)
