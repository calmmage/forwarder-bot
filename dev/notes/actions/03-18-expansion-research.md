Research results for forwarder-bot expansion, 2025-03-18

---

## Branch Status

`rework-to-middleware` already merged into main (PR #2). Safe to keep or delete branch.

## Crash Root Cause

`handler.py:68` — `messages[0].text.startswith("/")` crashes when text is None (any media message).
Also `handler.py:147` — date wrapped in list causing `[[timestamp]]` output.

## Sender Detection

`forward_origin` API (aiogram) solves hidden users:
- `MessageOriginUser` → `sender_user.full_name`
- `MessageOriginHiddenUser` → `sender_user_name` (works even with privacy settings!)
- `MessageOriginChat` → `sender_chat.title`
- `MessageOriginChannel` → `chat.title`
- Fallback: `forward_from` → `forward_sender_name` → `"unknown user"`

Covers 99% of cases. Interactive labeling only needed for edge cases (requires botspot `ask_user`).

## Media Support

Media types to handle: photo, video, document, voice, video_note, sticker, audio.
Text extraction: `message.caption or message.text`, media indicator like `[Photo]`.
Media groups: same `media_group_id`, already batched by the 500ms queue delay.
Forwarding back: `bot.copy_message()` — no download needed.

## Output Format Options

| Format | Approach | Media handling |
|--------|----------|---------------|
| Plain text | Improved `compose_messages()` | `[Photo]` indicators |
| HTML doc | Self-contained with inline CSS, chat bubbles | `<img>` base64 or placeholder |
| PDF | weasyprint renders the HTML | Same as HTML |
| telegra.ph | Telegraph-compatible HTML subset | Upload to telegra.ph CDN |
| GitHub Gist | Markdown via httpx + GitHub token | Text indicators only |
| Media forward | `bot.copy_message()` per media msg | Original media preserved |

## Conversation Styling — Chat Bubbles

Decision: WhatsApp-style chat bubbles.
- 2 participants: left/right alignment
- 3+ participants: all left-aligned, colored backgrounds per participant
- Sender name bold, timestamp small/muted
- Optional censoring via `CensorConfig(name_map={...}, auto_anonymize=True)`

## Framework Migration

Decision: migrate from `bot_lib` to `botspot`.
- Enables `ask_user_choice`, `send_safe`, middleware, `commands_menu`
- Follow botspot-template structure
- Also migrate poetry → uv

## Botspot Components Available

- `send_safe` — handles long text, media, parse mode fallback
- `ask_user_choice` — inline buttons with callback, timeout, FSMContext
- `ask_user` — free text input
- `SimpleUserCache` — user tracking middleware
- `markdown_to_html` — mistune-based conversion
- `commands_menu` — auto-registers bot commands
- `error_handler` — middleware for error handling

## Dependencies to Add

- `weasyprint` — PDF generation (needs `libpango`, `libcairo` in Docker)
- `httpx` — HTTP client for Gist API, telegraph
- `telegraph` — telegra.ph publishing (or raw httpx)
- `botspot` — replace `bot_lib`

## Implementation Order

1. Fix crashes + media support (handler.py)
2. Sender detection (handler.py)
3. Botspot migration
4. Formatters + format selection UI
5. Chat bubble HTML/PDF styling
6. Hetzner deploy
7. LLM analyzer, personal integrations
