def build_context(chunks):

    context_parts = []

    for chunk in chunks:

        doc_name = chunk["metadata"][
            "document_name"
        ]

        chunk_index = chunk["metadata"][
            "chunk_index"
        ]

        context_parts.append(
            f"""
[Document: {doc_name}]
[Chunk: {chunk_index}]

{chunk['content']}
"""
        )

    return "\n\n".join(context_parts)