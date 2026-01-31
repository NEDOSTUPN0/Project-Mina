import os

TRIGGER_WORD = "nyx"
SESSION_TIMEOUT = 600
SUMMARY_THRESHOLD = 10
MAX_QUEUE_SIZE = 3
MAX_PER_MINUTE = 3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTRUCTIONS_PATH = os.path.join(BASE_DIR, "data", "instructions.txt")
RULES_PATH = os.path.join(BASE_DIR, "data", "rules.txt")
STATE_FILE_PATH = os.path.join(BASE_DIR, "data", "session_state.json")
