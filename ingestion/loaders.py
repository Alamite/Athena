from pathlib import Path


def load_markdown_documents(data_dir: str):
    documents = []

    for file_path in Path(data_dir).glob("*.md"):
        content = file_path.read_text(encoding="utf-8")

        documents.append(
            {
                "document_name": file_path.stem,
                "source": str(file_path),
                "content": content,
            }
        )

    return documents