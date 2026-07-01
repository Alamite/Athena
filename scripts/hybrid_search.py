from retrieval.hybrid_retriever import (
    HybridRetriever
)

retriever = HybridRetriever()

results = retriever.retrieve(
    input("Question: ")
)

for i, result in enumerate(
    results[:10],
    start=1
):
    print("\n")
    print(f"Rank {i}")

    print(
        result["metadata"][
            "document_name"
        ]
    )

    print(
        result["content"][:200]
    )