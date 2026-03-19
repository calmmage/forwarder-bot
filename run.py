from dotenv import load_dotenv

load_dotenv()

from forwarder_bot.bot import bot, dp


if __name__ == "__main__":
    dp.run_polling(bot)
