import re

class ChatParser:
    def __init__(self):
        self.patterns = [
            r"^<(?P<user>\w+)> (?P<msg>.*)$", # vanilla, global
            r"^(?P<user>\w+) (?:whispers to you|шепчет вам): (?P<msg>.*)$", #vanilla, DM
            r"^.\s+(?P<user>\w+)\s+>\s+(?P<msg>.*)$", # EP, global
            r"^.\s+(?P<user>\w+)\s+→\s+(?:Вы|You|.*?):\s+(?P<msg>.*)$" # EP, DM
        ]

    def parse(self, text):
        for pattern in self.patterns:
            match = re.match(pattern, text)
            if match:
                return match.group("user"), match.group("msg")
        return None, None
