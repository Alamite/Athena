import os
import tempfile
# from pathlib import path
from langchain_core.documents import Document

from langchain_community.document_loaders import (TextLoader, PyPDFLoader)



def load_text_file():

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        temp_file.write(b"This is a sample")
        temp_file_path = temp_file.name

    try:
        loader = TextLoader(temp_file_path)
        documents = loader.load()

        for doc in documents:
            print(doc.page_content)

    finally:
        os.remove(temp_file_path)


def load_pdf_file(file_path: str):
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    for i, doc in enumerate(documents):
        print(f"Doc {i+1} Preview: {doc.page_content[:100]}")


if __name__ == "__main__":
    load_pdf_file("./docs/sample.pdf")