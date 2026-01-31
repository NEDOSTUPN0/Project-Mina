import asyncio
import time
from collections import deque
import minescript
from .config import MAX_QUEUE_SIZE, MAX_PER_MINUTE, TRIGGER_WORD

class RequestWorker:
    def __init__(self, ai_handler, session_manager):
        self.ai = ai_handler
        self.session = session_manager
        self.user_queues = {}
        self.user_rates = {}
        self.global_queue = asyncio.Queue()

    async def add_request(self, user, message):
        now = time.time()
        if user not in self.user_rates:
            self.user_rates[user] = deque()
        
        while self.user_rates[user] and now - self.user_rates[user][0] > 60:
            self.user_rates[user].popleft()

        if len(self.user_rates[user]) >= MAX_PER_MINUTE:
            minescript.execute(f"/msg {user} {TRIGGER_WORD} Пожалуйста, подождите. Лимит 3 запроса в минуту.")
            return

        if user not in self.user_queues:
            self.user_queues[user] = asyncio.Queue()
            asyncio.create_task(self.process_user_queue(user))

        if self.user_queues[user].qsize() >= MAX_QUEUE_SIZE:
            minescript.execute(f"/msg {user} {TRIGGER_WORD} Очередь заполнена (макс 3). Подождите завершения.")
            return

        self.user_rates[user].append(now)
        await self.user_queues[user].put(message)

    async def process_user_queue(self, user):
        while True:
            msg = await self.user_queues[user].get()
            await self.global_queue.put((user, msg))
            self.user_queues[user].task_done()

    async def global_worker_loop(self):
        while True:
            user, msg = await self.global_queue.get()
            try:
                await self.session.add_to_history("user", f"{user}: {msg}")
                
                response = await self.ai.ask(self.session.history, msg)
                
                await self.session.add_to_history("assistant", response)
                
                minescript.chat(f"{user}, {response}")
                
            except Exception as e:
                minescript.log(f"AI Error: {e}")
            finally:
                self.global_queue.task_done()
