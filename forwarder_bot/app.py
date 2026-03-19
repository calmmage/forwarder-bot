import asyncio
from collections import defaultdict


class App:
    def __init__(self):
        self.user_message_queue = defaultdict(asyncio.Queue)
        self.user_lock = defaultdict(asyncio.Lock)
