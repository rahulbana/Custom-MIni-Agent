# helper to load prompts
import os

PROMPT_DIR = os.path.dirname(__file__)

def load_prompt(name: str) -> str:
    with open(os.path.join(PROMPT_DIR, f"{name}.txt"), "r") as f:
        return f.read()