
def precision_at_k(
    retrieved_chunks: list,
    relevant_chunks: set,
    k: int
) -> float:

    retrieved = retrieved_chunks[:k]

    if k <= 0:
        raise ValueError("k must be greater than zero")

    relevant_retrieved = sum(
        1 for chunk in retrieved
        if chunk in relevant_chunks
    )

    return relevant_retrieved / k


def recall_at_k(
    retrieved_chunks: list,
    relevant_chunks: set,
    k: int
) -> float:

    if not relevant_chunks:
        raise ValueError("Ground truth cannot be empty")

    retrieved = retrieved_chunks[:k]

    relevant_retrieved = sum(
        1 for chunk in retrieved
        if chunk in relevant_chunks
    )

    return relevant_retrieved / len(relevant_chunks)


def reciprocal_rank(
    retrieved_chunks: list,
    relevant_chunks: set
) -> float:

    for rank, chunk in enumerate(retrieved_chunks, start=1):

        if chunk in relevant_chunks:
            return 1 / rank

    return 0.0


def mean_reciprocal_rank(
    reciprocal_ranks: list[float]
) -> float:

    if not reciprocal_ranks:
        return 0.0

    return sum(reciprocal_ranks) / len(reciprocal_ranks)
