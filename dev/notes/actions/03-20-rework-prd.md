PRD / work log for the forwarder-bot rework session, 2026-03-20

---

## What was done

### 1. Codebase exploration & research

Explored the full project: handler.py, app.py, bot.py, run.py, pyproject.toml, dev/todo.md, tests, Dockerfile, CI.
Also explored botspot framework (components, middleware, template) and botspot-template for migration reference.

Key findings:
- Bot collects forwarded Telegram messages, batches them via asyncio Queue with 500ms delay, outputs formatted text
- Built on aiogram + bot_lib (custom framework) + calmlib
- `rework-to-middleware` branch already merged into main (PR #2) — branch is safe, no need to discard
- Two bugs found: crash on media messages, date formatting bug

### 2. Branch review

`rework-to-middleware` was already merged. It split monolithic `lib.py` into `app.py` + `handler.py`, updated to newer bot-lib API, added dev/todo.md with photo/video plans, added middleware experiments in dev/draft/.

Verdict: keep the branch, all changes are good.

### 3. Bugs fixed

**Crash on media messages** — `handler.py:68`: `messages[0].text.startswith("/")` crashes when `text` is None (photos, videos, any media-only message). Fixed with null check.

**Date formatting bug** — `handler.py:147`: `date = [format_message_date(message.forward_date)]` wrapped result in a list, causing `[[Mar 15, 14:32]]` in output. Fixed by removing list wrapper.

### 4. Media support added

New `_get_message_text(message)` function replaces `_extract_message_text()`:
- Returns media type indicators: `[Photo]`, `[Video: name]`, `[Document: name]`, `[Voice message]`, `[Video note]`, `[Sticker emoji]`, `[Audio: name]`
- Extracts `message.caption or message.text`
- Combines: `[Photo] caption text here`
- Fallback: `[Unsupported content]`

This replaces the old `_extract_message_text()` from bot_lib's Handler which tried to do voice transcription and file downloads — we just want text representation.

### 5. Unknown user detection fixed

New `_get_sender_name(message)` function using `forward_origin` API:
- `MessageOriginUser` → `sender_user.full_name` (normal forwarded messages)
- `MessageOriginHiddenUser` → `sender_user_name` (privacy settings enabled — this is the key fix, covers 99% of "unknown user" cases)
- `MessageOriginChat` → `sender_chat.title`
- `MessageOriginChannel` → `chat.title`
- Fallback chain: `forward_from` → `forward_sender_name` → `"unknown user"`

Previously the bot showed "unknown user" for anyone with privacy settings. Now it shows their display name.

### 6. Migrated from bot_lib to botspot

**Why**: bot_lib was incompatible with current calmlib (broken `get_logger` import). botspot is the actively maintained framework with better components.

**What changed**:

`app.py` — stripped to plain class, no more `bot_lib.App` inheritance:
```python
class App:
    def __init__(self):
        self.user_message_queue = defaultdict(asyncio.Queue)
        self.user_lock = defaultdict(asyncio.Lock)
```

`handler.py` — converted from `bot_lib.Handler` class to aiogram Router + standalone functions:
- `MyHandler` class → module-level `router = Router()` + `@router.message()` decorated `chat_handler`
- `self.logger` → `loguru.logger`
- `self.reply_safe()` / `self._send_as_file()` → `botspot.utils.send_safe()`
- `self._extract_message_text()` → `_get_message_text()` (standalone function)
- All helper methods → standalone functions (`_get_sender_name`, `_get_message_text`, `compose_messages`, `format_message_date`)

`bot.py` — rewired to botspot:
- `BotManager` from bot_lib → `BotManager` from botspot
- `create_bot()` → `Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])`
- `bot_manager.setup_dispatcher(dp, extra_handlers=handlers)` → `dp.include_router(router)` + `bm.setup_dispatcher(dp)`
- App passed via `dp["app"] = app` (aiogram workflow data injection)

`run.py` — simplified:
- `app.run(dp=dp, bot=bot)` → `dp.run_polling(bot)`

### 7. Infrastructure migration

- Python 3.11 → 3.12 (calmlib uses PEP 695 type syntax `def func[T: BaseModel]()`)
- Poetry → uv (pyproject.toml rewritten with hatchling build backend)
- Dependencies: replaced `bot_lib` with `botspot`, added `pymongo` (transitive dep from calmlib)
- `bot_lib` kept in `extras` dependency group for reference

### 8. Tasks & future plans saved

`dev/notes/tasks.md` — user's original task list preserved verbatim.
`dev/notes/actions/03-18-expansion-research.md` — detailed research results.

Future plans added:
- Rename to conversations / conversations-extractor bot
- Use mtproto telethon client to load recent conversations directly
- Chat summarization / feed — extract wisdom, knowledge, advice from high-quality chats

---

## Architecture after rework

```
forwarder_bot/
  app.py        — App class with per-user message queue + lock
  bot.py        — Bot/Dispatcher/BotManager setup, wires router
  handler.py    — Router with chat_handler, message composition functions
  __init__.py   — version
run.py          — entry point, dp.run_polling(bot)
```

Message flow:
1. User forwards messages → `chat_handler()` receives each
2. Message queued per user (`app.user_message_queue[user_id]`)
3. Lock acquired, 500ms delay to collect batch
4. All queued messages grabbed, sorted by date
5. `compose_messages()` formats with timestamps + sender names + media indicators
6. Output via `send_safe()` (handles long text, splitting, file mode)

## Design decisions made

- **Botspot over bot_lib**: bot_lib is broken with current calmlib, botspot is actively maintained and has better components (send_safe, ask_user_choice, error_handler middleware)
- **Standalone functions over Handler class**: simpler, no inheritance needed, works naturally with aiogram Router
- **forward_origin API over forward_from**: handles privacy settings, covers hidden users
- **Media text indicators over downloading**: `[Photo]` is sufficient for text output, downloading adds complexity for later phases
- **Chat bubbles for HTML export**: decided WhatsApp-style for future formatter work

## What's next

Phase 4: Output format selection — `forwarder_bot/formatters.py` with `ConversationMessage` model, format_text/html/pdf/telegraph/gist functions, inline button selection via `ask_user_choice()`

Phase 5: Chat bubble HTML/PDF — self-contained HTML with inline CSS, weasyprint for PDF

Phase 6-7: Deploy, LLM analyzer, personal integrations, telethon client, chat summarization
