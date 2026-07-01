import requests

from generation.prompts import SYSTEM_PROMPT


class AnswerGenerator:

    def __init__(self):
        self.url = "http://localhost:11434/api/generate"
        self.model = "llama3.1:8b"

    def generate(self, question, context):

        prompt = SYSTEM_PROMPT.format(context=context)

        full_prompt = f"""{prompt}

Question:
{question}
"""

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False
        }

        response = requests.post(
            self.url,
            json=payload,
            timeout=(10, 300)
        )

        response.raise_for_status()

        return response.json()["response"]