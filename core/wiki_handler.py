import os
from .config import BASE_DIR

WIKI_DIR = os.path.join(BASE_DIR, "data", "wiki")

class WikiHandler:
    @staticmethod
    def get_all_pages():
        pages = []
        if not os.path.exists(WIKI_DIR):
            return pages
            
        for root, _, files in os.walk(WIKI_DIR):
            for file in files:
                if file.endswith(".txt"):
                    rel_path = os.path.relpath(os.path.join(root, file), WIKI_DIR)
                    pages.append(rel_path.replace(".txt", ""))
        return pages

    @staticmethod
    def read_page(page_name):
        file_path = os.path.join(WIKI_DIR, f"{page_name}.txt")
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            return f"Error: Page '{page_name}' not found."
        except Exception as e:
            return f"Error reading page: {e}"
