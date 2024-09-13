import asyncio
import os
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram import Bot
from aiogram import Dispatcher
from aiogram import Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from dotenv import load_dotenv


class CounterMiddleware(BaseMiddleware):
    def __init__(self):
        self.counter = 0

    async def __call__(
        self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]
    ) -> Any:
        self.counter += 1
        data["counter"] = self.counter
        return await handler(event, data)


router = Router()
router.message.middleware(CounterMiddleware())


@router.message()
async def message_handler(message: Message, counter: int):
    await message.answer(f"This is message number {counter}")


load_dotenv()
# Bot token can be obtained via https://t.me/BotFather
token = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(
    token,  # parse_mode=ParseMode.HTML
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

if __name__ == "__main__":

    # from aiogram import executor

    dp = Dispatcher()
    dp.include_router(router)

    # executor.start_polling(dp, skip_updates=True)
    asyncio.run(dp.start_polling(bot))
