import json
import os
import openai
from core.wiki_handler import WikiHandler
from core.config import INSTRUCTIONS_PATH, RULES_PATH

class AIHandler:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.wiki = WikiHandler()
        
    def get_static_prompt(self):
        with open(INSTRUCTIONS_PATH, "r", encoding="utf-8") as f:
            inst = f.read()
        with open(RULES_PATH, "r", encoding="utf-8") as f:
            rules = f.read()

        pages = self.wiki.get_all_pages()
        pages_list = ", ".join(pages)

        return (
            f"System Instructions:\n{inst}\n\n"
            f"Server Rules:\n{rules}\n\n"
            f"Available Wiki Pages: {pages_list}\n"
            "If you need more info to answer, use 'get_wiki_page' tool."
        )
        
    async def ask(self, history, current_msg):
        messages = [{"role": "system", "content": self.get_static_prompt()}]
        messages.extend(history)
        messages.append({"role": "user", "content": current_msg})
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_wiki_page",
                    "description": "Get detailed information from the server wiki.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "page_name": {
                                "type": "string", 
                                "description": "The name of the wiki page to read.",
                                "enum": self.wiki.get_all_pages()
                            }
                        },
                        "required": ["page_name"]
                    }
                }
            }
        ]

        response = await self.client.chat.completions.create(
            model="gpt-5.1",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        
        response_message = response.choices[0].message

        if response_message.tool_calls:
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                if tool_call.function.name == "get_wiki_page":
                    args = json.loads(tool_call.function.arguments)
                    page_content = self.wiki.read_page(args.get("page_name"))
                    
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": "get_wiki_page",
                        "content": str(page_content)
                    })
            
            final_response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=250
            )
            return final_response.choices[0].message.content

        return response_message.content if response_message.content else ""

    async def summarize(self, history):
        text = ""
        for m in history:
            role_name = "Bot" if m['role'] == 'assistant' else "Player"
            if m['role'] == 'system': role_name = "Context"
            text += f"{role_name}: {m['content']}\n"

        prompt = (
            "Update the summary of this conversation. "
            "Below is the text including the old summary and new messages. "
            "Create one new, concise summary that combines everything important. "
            "Ignore greetings and fluff.\n\n"
            f"{text}"
        )
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return response.choices[0].message.content
