MAX_DISTANCE = 0.8


def filter_chunks(chunks):

    return [
        chunk
        for chunk in chunks
        if chunk["distance"] < MAX_DISTANCE
    ]