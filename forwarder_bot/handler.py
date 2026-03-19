import asyncio
from datetime import datetime

from aiogram import Router
from aiogram.types import (
    Message,
    MessageOriginChannel,
    MessageOriginChat,
    MessageOriginHiddenUser,
    MessageOriginUser,
)
from botspot.utils import send_safe
from loguru import logger

from forwarder_bot.app import App

router = Router()

# 500 ms delay to batch messages
MULTI_MESSAGE_DELAY = 0.5


def format_message_date(dt: datetime) -> str:
    """Format datetime in a human-friendly way:
    - Today: only time (13:45)
    - This year: date without year (Mar 15)
    - Earlier: full date (Mar 15, 2023)
    """
    now = datetime.now()

    if dt.date() == now.date():
        return dt.strftime("%H:%M")
    elif dt.year == now.year:
        return dt.strftime("%b %d, %H:%M")
    else:
        return dt.strftime("%b %d %Y, %H:%M")


def _get_sender_name(message: Message) -> str:
    """Extract sender name, handling privacy settings via forward_origin."""
    if message.forward_origin:
        origin = message.forward_origin
        if isinstance(origin, MessageOriginUser):
            user = origin.sender_user
            return user.full_name or user.username or str(user.id)
        elif isinstance(origin, MessageOriginHiddenUser):
            return origin.sender_user_name
        elif isinstance(origin, MessageOriginChat):
            return origin.sender_chat.title or "unknown chat"
        elif isinstance(origin, MessageOriginChannel):
            return origin.chat.title or "unknown channel"
    if message.forward_from:
        return message.forward_from.full_name or message.forward_from.username or "unknown user"
    if message.forward_sender_name:
        return message.forward_sender_name
    return "unknown user"


def _get_message_text(message: Message) -> str:
    """Extract text content with media type indicators."""
    parts = []
    if message.photo:
        parts.append("[Photo]")
    elif message.video:
        parts.append(f"[Video: {message.video.file_name or 'video'}]")
    elif message.document:
        parts.append(f"[Document: {message.document.file_name or 'file'}]")
    elif message.voice:
        parts.append("[Voice message]")
    elif message.video_note:
        parts.append("[Video note]")
    elif message.sticker:
        emoji = message.sticker.emoji or ""
        parts.append(f"[Sticker {emoji}]")
    elif message.audio:
        parts.append(f"[Audio: {message.audio.file_name or 'audio'}]")

    text_content = message.caption or message.text
    if text_content:
        parts.append(text_content)

    return " ".join(parts) if parts else "[Unsupported content]"


def compose_messages(
    messages: list[Message],
    include_usernames=True,
    include_timestamps=True,
    separator="\n\n~~~\n\n",
) -> str:
    text = ""
    for message in messages:
        try:
            parts = []
            if include_timestamps:
                dt = message.forward_date or message.date
                date = format_message_date(dt)
                parts += [f"[{date}]"]
            if include_usernames:
                parts += [_get_sender_name(message)]
            if parts:
                text += " ".join(parts) + ":\n"
            text += _get_message_text(message)
            text += separator
        except Exception:
            logger.exception("Failed to compose message")
            text += f"Failed to compose message\n{separator}"
    return text


# State: per-instance, shared via dp["app"]
send_as_file = False


@router.message()
async def chat_handler(message: Message, app: App):
    # skip commands
    if message.text and message.text.startswith("/"):
        return
    user = message.from_user.id
    queue = app.user_message_queue[user]
    await queue.put(message)

    async with app.user_lock[user]:
        await asyncio.sleep(MULTI_MESSAGE_DELAY)

        messages = []
        while not queue.empty():
            item = await queue.get()
            messages.append(item)
        if not messages:
            logger.debug("Messages already processed by another handler")
            return

        messages.sort(key=lambda x: x.date)
        await message.answer(f"Received {len(messages)} messages")

        text = compose_messages(messages)
        if send_as_file:
            await send_safe(message.bot, chat_id=message.chat.id, text=text, send_as_file=True)
        else:
            await send_safe(message.bot, chat_id=message.chat.id, text=text)
