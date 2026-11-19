
import json
from pathlib import Path
from collections import defaultdict

from app.services.retrieval_service import retrieve_documents

from app.evaluation.evaluation_metrics import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    mean_reciprocal_rank
)


BASE_DIR = Path(__file__).resolve().parents[1]

DATASET_PATH = BASE_DIR / "uploads" / "evealuation_dataset.json"

K = 3

RETRIEVAL_TYPES = [
    "similarity",
    "bm25",
    "hybrid_search"
]


def get_chunk_id(document):

    return (
        document.metadata.get("document_id"),
        document.metadata.get("chunk_index")
    )


def load_dataset():

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_strategy(dataset, retrieval_type):

    results = []

    for item in dataset:

        query = item["query"]

        relevant_chunks = {
            (
                chunk["document_id"],
                chunk["chunk_index"]
            )
            for chunk in item["relevant_chunks"]
        }

        # Retrieve documents
        retrieved_documents = retrieve_documents(
            query=query,
            k=K,
            retrieval_type=retrieval_type
        )

        retrieved_chunks = [
            get_chunk_id(doc)
            for doc in retrieved_documents
        ]

        # Calculate metrics
        precision = precision_at_k(
            retrieved_chunks,
            relevant_chunks,
            K
        )

        recall = recall_at_k(
            retrieved_chunks,
            relevant_chunks,
            K
        )

        rr = reciprocal_rank(
            retrieved_chunks,
            relevant_chunks
        )

        results.append({
            "query": query,
            "precision@k": precision,
            "recall@k": recall,
            "reciprocal_rank": rr
        })

    # Calculate aggregate metrics
    avg_precision = sum(
        result["precision@k"] for result in results
    ) / len(results)

    avg_recall = sum(
        result["recall@k"] for result in results
    ) / len(results)

    mrr = mean_reciprocal_rank([
        result["reciprocal_rank"]
        for result in results
    ])

    return {
        "retrieval_type": retrieval_type,
        "precision@k": avg_precision,
        "recall@k": avg_recall,
        "mrr": mrr,
        "query_results": results
    }


def main():

    dataset = load_dataset()

    if not dataset:
        raise ValueError("Evaluation dataset is empty.")

    for item in dataset:
        if not item.get("relevant_chunks"):
            raise ValueError(
                f"Missing ground truth for query: {item['query']}"
            )

    all_results = {}

    for retrieval_type in RETRIEVAL_TYPES:

        print(f"\nEvaluating: {retrieval_type}")

        result = evaluate_strategy(
            dataset,
            retrieval_type
        )

        all_results[retrieval_type] = result

        print(
            f"Precision@{K}: {result['precision@k']:.4f}"
        )

        print(
            f"Recall@{K}: {result['recall@k']:.4f}"
        )

        print(
            f"MRR: {result['mrr']:.4f}"
        )

    print("\n========== COMPARISON ==========")

    print(
        f"{'Strategy':<20}"
        f"{'Precision':<15}"
        f"{'Recall':<15}"
        f"{'MRR':<15}"
    )

    for strategy, result in all_results.items():

        print(
            f"{strategy:<20}"
            f"{result['precision@k']:<15.4f}"
            f"{result['recall@k']:<15.4f}"
            f"{result['mrr']:<15.4f}"
        )

    # Save detailed evaluation results
    output_path = BASE_DIR / "evaluation" / "results.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            all_results,
            file,
            indent=4
        )

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
