def format_citations(chunks):

    citations = []

    for chunk in chunks:

        meta = chunk["metadata"]

        citations.append(
            {
                "document":
                    meta["document_name"],
                "chunk":
                    meta["chunk_index"]
            }
        )

    return citations

def generate_citations(chunks):

    citations = []

    seen = set()

    for chunk in chunks:

        doc = chunk["metadata"][
            "document_name"
        ]

        idx = chunk["metadata"][
            "chunk_index"
        ]

        key = (doc, idx)

        if key not in seen:

            citations.append(
                {
                    "document": doc,
                    "chunk": idx
                }
            )

            seen.add(key)

    return citations