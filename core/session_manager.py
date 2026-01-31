import asyncio
import time
import json
import os
import tempfile
import minescript
from .config import SESSION_TIMEOUT, SUMMARY_THRESHOLD, STATE_FILE_PATH

class SessionManager:
    def __init__(self, ai_handler):
        self.ai = ai_handler
        self.lock = asyncio.Lock()
        
        self.history = []
        self.pending_count = 0
        self.last_activity = time.time()
        
        self.load_state()

    def load_state(self):
        if os.path.exists(STATE_FILE_PATH):
            try:
                with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.history = data.get("history", [])
                    self.last_activity = data.get("last_activity", time.time())
                    self.pending_count = data.get("pending_count", 0)
                minescript.log("Session state loaded from file.")
            except Exception as e:
                minescript.log(f"Error loading state file: {e}")

    def save_state(self):
        try:
            dir_name = os.path.dirname(STATE_FILE_PATH)
            fd, temp_path = tempfile.mkstemp(dir=dir_name, text=True)
            
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump({
                    "history": self.history,
                    "last_activity": self.last_activity,
                    "pending_count": self.pending_count
                }, f, ensure_ascii=False, indent=4)
            
            os.replace(temp_path, STATE_FILE_PATH)
        except Exception as e:
            minescript.log(f"Critical saving error: {e}")

    async def add_to_history(self, role, content):
        async with self.lock:
            self.history.append({"role": role, "content": content})
            if role == "user":
                self.pending_count += 1
            self.last_activity = time.time()
            self.save_state()

    async def check_timeout_loop(self):
        while True:
            await asyncio.sleep(60)
            if self.history and (time.time() - self.last_activity > SESSION_TIMEOUT):
                await self.end_session()

    async def end_session(self):
        async with self.lock:
            if not self.history:
                return

            if self.pending_count >= SUMMARY_THRESHOLD:
                try:
                    
                    self.history = [{"role": "system", "content": f"Summary of previous messages: {summary}"}]
                    self.pending_count = 0
                    minescript.log("The session has been summarized.")
                except Exception as e:
                    minescript.log(f"Error while summarizing: {e}")
            else:
                minescript.log("Session ended (not enough messages for summary, history cleared).") 

            self.last_activity = time.time()
            self.save_state()
