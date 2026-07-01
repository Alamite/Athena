from retrieval.bm25_retriever import (
    BM25Retriever
)

retriever = BM25Retriever()

results = retriever.search(
    input("Question: ")
)

for chunk, score in results:

    print("\n")
    print(score)

    print(
        chunk["document_name"]
    )

    print(
        chunk["content"][:300]
    )