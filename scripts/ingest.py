import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json

from ingestion.loaders import load_markdown_documents
from ingestion.pipeline import process_documents


def main():

    documents = load_markdown_documents(
        "data/raw"
    )

    chunks = process_documents(documents)

    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "chunks.json"

    with open(output_file, "w", encoding="utf-8") as f:

        json.dump(
            [chunk.to_dict() for chunk in chunks],
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"Generated {len(chunks)} chunks")
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()