from retrieval.retriever import Retriever
from retrieval.filters import filter_chunks
from retrieval.context_builder import build_context

from generation.answer_generator import (
    AnswerGenerator
)

from generation.citations import (
    generate_citations
)


def main():

    question = input(
        "Question: "
    )

    retriever = Retriever()

    chunks = retriever.retrieve(
        question
    )

    chunks = filter_chunks(
        chunks
    )

    if not chunks:

        print(
            "I cannot answer based on the retrieved documents."
        )

        return

    context = build_context(
        chunks
    )

    generator = AnswerGenerator()

    answer = generator.generate(
        question,
        context
    )

    citations = generate_citations(
        chunks
    )

    print("\nANSWER\n")
    print(answer)

    print("\nCITATIONS\n")

    for i, citation in enumerate(
        citations,
        start=1
    ):
        print(
            f"[{i}] "
            f"{citation['document']} "
            f"(chunk {citation['chunk']})"
        )


if __name__ == "__main__":
    main()