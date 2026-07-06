import logging

from openai import OpenAI

logger = logging.getLogger(__name__)


class QueryRewriter:
    def __init__(
        self,
        model: str = "llama3.1:8b",
        base_url: str = "http://localhost:11434/v1",
    ):
        self.client = OpenAI(
            base_url=base_url,
            api_key="ollama",  # Required but ignored by Ollama
        )
        self.model = model

    def rewrite(
        self,
        query: str,
        n: int = 4,
    ):
        prompt = f"""
Generate {n} alternative search queries for retrieving
documents relevant to the user question below.

Rephrase using synonyms and closely related terms
(e.g. "space" -> "storage" when talking about electronic
devices), so the queries can match different wording than
the original question while keeping the same meaning.

User Question:
{query}

Return exactly {n} queries, one per line, with no
numbering or extra commentary.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            queries = response.choices[0].message.content.splitlines()

            queries = [
                q.strip("-* \t")
                for q in queries
                if q.strip("-* \t")
            ]

            print(
                queries[:n]
            )

            return queries[:n]

        except Exception:
            logger.exception(
                "Query rewriting failed, falling back to original query only"
            )
            return [query]