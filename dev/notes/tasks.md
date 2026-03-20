# Forwarder Bot Tasks

- [ ] Unrecognized people - offer to label them manually, one by one
- [ ] Review current git branch - do we discard it? Current version is working fine
- [ ] After getting the messages, offer multiple possible scenarios
  - send as text / markdown (what to do with media? Send back as single media group?)
  - make a nicely formatted html / pdf / what?
  - publish on the web - e.g. github gist or telegra.ph blogging platform
  - Think and research / design some nice way how to make interview-style q&a or simply a reasonably formatted conversation, with clear visuals who said what. Kinda like screenshots would, but as a doc and with more censoring flexibility.
- [ ] Improve stability - add support for media content (we crash on it now for some reason)
- [ ] Deploy on a new hetzner machine
- [ ] Add structural llm analyzer? For more complex chats
- [ ] Think about personal integrations - saving to knowledge base etc.
- [ ] Rename to conversations / conversations-extractor bot
- [ ] Use mtproto telethon client to load recent conversations from private and small group chats / owned instead of having to forward. Then select from a list and tune explicit set of messages.
- [ ] Chat summarization / feed feature - extract wisdom and info from chats, knowledge and data, advice (especially high-quality chats)
