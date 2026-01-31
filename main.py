import asyncio
import minescript
from core.config import TRIGGER_WORD
from core.parser import ChatParser
from core.openai_handler import AIHandler
from core.session_manager import SessionManager
from core.request_worker import RequestWorker
from dotenv import load_dotenv

load_dotenv()

async def main():
    parser = ChatParser()
    ai = AIHandler()
    session = SessionManager(ai)
    worker = RequestWorker(ai, session)

    asyncio.create_task(session.check_timeout_loop())
    asyncio.create_task(worker.global_worker_loop())

    minescript.echo(f"AI Bot started. Trigger: {TRIGGER_WORD}")

    with minescript.EventQueue() as event_queue:
        event_queue.register_chat_listener()
        event_queue.register_world_listener()
        
        while True:
            try:
                event = event_queue.get(block=True, timeout=0.1)
                
                if event.type == "chat":
                    user, msg = parser.parse(event.message)
                    if user and msg:
                        msg_low = msg.lower()
                        is_triggered = msg_low.startswith(TRIGGER_WORD) or f"@{TRIGGER_WORD}" in msg_low
                        if is_triggered:
                            await worker.add_request(user, msg)
                
                elif event.type == "world":
                    if not event.connected:
                        minescript.log("World disconnect detected. Forcing state save...")
                        session.save_state()
                        break

            except Exception:
                pass
            
            await asyncio.sleep(0.01)

if __name__ == "__main__":
    asyncio.run(main())
