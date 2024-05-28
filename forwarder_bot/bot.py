from aiogram import Dispatcher
from dotenv import load_dotenv
from forwarder_bot.lib import MyApp, MainHandler

from bot_lib import (
    BotConfig,
    setup_dispatcher,
)
from bot_lib.demo import create_bot, run_bot

plugins = []
app = MyApp(plugins=plugins)
bot_config = BotConfig(app=app)

# set up dispatcher
dp = Dispatcher()

my_handler = MainHandler()
handlers = [my_handler]
setup_dispatcher(dp, bot_config, extra_handlers=handlers)

load_dotenv()
bot = create_bot()

if __name__ == "__main__":
    run_bot(dp, bot)
