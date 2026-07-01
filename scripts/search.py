from embeddings.embedder import Embedder
from vectorstore.chroma_store import ChromaStore


def main():

    query = input("Question: ")

    embedder = Embedder()

    query_embedding = embedder.embed(
        [query]
    )[0]

    store = ChromaStore()

    results = store.search(
        query_embedding=query_embedding,
        top_k=5
    )

    print("\nResults:\n")

    for i, doc in enumerate(results["documents"][0]):

        metadata = results["metadatas"][0][i]

        print("=" * 80)

        print(
            f"Document: "
            f"{metadata['document_name']}"
        )

        print(
            f"Chunk: "
            f"{metadata['chunk_index']}"
        )

        print()

        print(doc[:500])


if __name__ == "__main__":
    main()