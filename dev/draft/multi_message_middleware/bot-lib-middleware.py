from typing import Callable, Dict, Awaitable, Any

from calmapp import App
from aiogram.types import Message
from aiogram import Router

from bot_lib import Handler, HandlerDisplayMode


class MyApp(App):
    __doc__ = (
        """This is an amazing application that I developed in my free time! For now it just exists, and that is good!"""
    )

    name: str = "My amazing app"
    # Sample
    start_message = "Hello! I am {name}. {description}"

    @property
    def description(self):
        return self.__doc__


class MyHandler(Handler):
    name = "main"
    display_mode = HandlerDisplayMode.FULL
    commands = {
        # "dummy_command_handler": "dummy_command",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0

    has_chat_handler = True

    async def chat_handler(self, message: Message, app: MyApp, counter: int, **kwargs):
        output_str = f"This is message number {counter}"
        await self.reply_safe(message, output_str)

    async def my_middleware(
        self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]
    ) -> Any:
        self.counter += 1
        data["counter"] = self.counter
        return await handler(event, data)

    def setup_router(self, router: Router):
        super().setup_router(router)
        router.message.middleware(self.my_middleware)


if __name__ == "__main__":

    from aiogram import Dispatcher, Router
    from bot_lib import BotManager
    from bot_lib.utils import create_bot
    from dotenv import load_dotenv

    from forwarder_bot.app import MyApp
    from forwarder_bot.handler import MyHandler

    load_dotenv()

    app = MyApp()
    bot_manager = BotManager(app=app)

    dp = Dispatcher()

    my_handler = MyHandler()
    handlers = [my_handler]
    bot_manager.setup_dispatcher(dp, extra_handlers=handlers)

    bot = create_bot()

    app.run(dp, bot)
