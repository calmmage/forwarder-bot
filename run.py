from dotenv import load_dotenv

load_dotenv()
from forwarder_bot.bot import bot, dp, app


if __name__ == "__main__":
    app.run(dp=dp, bot=bot)
