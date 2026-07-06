def reciprocal_rank_fusion(
    *result_lists,
    k=60
):
    scores = {}

    all_chunks = {}

    for result_list in result_lists:

        for rank, chunk in enumerate(
            result_list
        ):
            chunk_id = chunk["id"]

            scores[chunk_id] = (
                scores.get(chunk_id, 0)
                + 1 / (k + rank + 1)
            )

            all_chunks[chunk_id] = chunk

    ranked_ids = sorted(
        scores.keys(),
        key=lambda x: scores[x],
        reverse=True
    )

    return [
        all_chunks[chunk_id]
        for chunk_id in ranked_ids
    ]