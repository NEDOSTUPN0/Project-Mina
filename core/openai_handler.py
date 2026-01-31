import openai
from .config import INSTRUCTIONS_PATH, RULES_PATH
import os

class AIHandler:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def get_static_prompt(self):
        with open(INSTRUCTIONS_PATH, "r", encoding="utf-8") as f:
            inst = f.read()
        with open(RULES_PATH, "r", encoding="utf-8") as f:
            rules = f.read()
        return f"System Instructions:\n{inst}\n\nServer Rules:\n{rules}"

    async def ask(self, history, current_msg):
        messages = [{"role": "system", "content": self.get_static_prompt()}]
        messages.extend(history)
        messages.append({"role": "user", "content": current_msg})
        
        response = await self.client.chat.completions.create(
            model="gpt-5.2",
            messages=messages,
            # max_completion_tokens=150
        )
        return response.choices[0].message.content

    async def summarize(self, messages_to_sum):
        text = "\n".join([f"{m['role']}: {m['content']}" for m in messages_to_sum])
        prompt = f"Make the most concise summary of this dialogue, keeping only the important details for future context:\n\n{text}"
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
