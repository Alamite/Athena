from openai import OpenAI


class QueryRewriter:

    def __init__(self):
        self.client = OpenAI()

    def rewrite(
        self,
        query: str
    ):

        prompt = f"""
Generate 4 alternative search queries
for retrieving documents.

User Question:
{query}

Return one query per line.
"""

        response = (
            self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
        )

        queries = (
            response
            .choices[0]
            .message.content
            .split("\n")
        )

        return [
            q.strip()
            for q in queries
            if q.strip()
        ]