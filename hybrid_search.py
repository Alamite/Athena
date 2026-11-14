from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_community.retrievers import BM25Retriever
# from langchain.retrievers import EnsambleRetriever
import tempfile

from dotenv import load_dotenv
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
MODEL = os.getenv("MODEL")

embeddings_model = OllamaEmbeddings(model = EMBEDDING_MODEL)

documents = [
    Document(
        page_content = "Product sku-90876 is our flagship phone with a 6.5-inch display, 128GB storage, and a 48MP camera.",
        metadata = {"source": "product_catalog.txt"}
    ),
    Document(
        page_content = "For network connectivity issues restart the device. If the problem persists, contact customer support.",
        metadata = {"source": "troubleshooting_guide.txt"}
    ),
    Document(
        page_content = "Error code E_CAM_Refused indicates that the camera module is not responding. Check the camera connection and try again.",
        metadata = {"source": "error_codes.txt"}
    ),
    Document(
        page_content = "The authentication process requires face ID or fingerprint verification. Ensure that the biometric sensors are clean and functional.",
        metadata = {"source": "authentication_guide.txt"}
    ),
    Document(
        page_content = "LOG_RAW give the full HDR images captured by the camera module. Use this command for advanced diagnostics.",
        metadata = {"source": "camera_commands.txt"}
    ),
    Document(
        page_content = "The admin settings allows you to ad apple id and manage device configurations. Navigate to 192.168.1.1 to access these options.",
        metadata = {"source": "admin_settings.txt"} 
    )
]


def create_kb():
    # splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50)
    # # for doc in documents:
    # chunks = splitter.split_documents([documents])

    vector_store = Chroma.from_documents(
            documents = documents,
            embedding = embeddings_model,
            persist_directory = tempfile.mkdtemp()
        )

    return vector_store


def hybrid_search():

    vector_store = create_kb()
    vector_retriever = vector_store.as_retriever(search_kwargs = {"k" : 3})

    bm25_retriever = BM25Retriever.from_documents(
        documents,
        k = 3
    )

    # ensemble_retriever = EnsambleRetriever(
    #     retrievers = [bm25_retriever, vector_retriever],
    #     weights = [0.5, 0.5]
    # )

    def test_query(query, name, retriever):
        print("\n\n")
        results = retriever.invoke(query)
        print(f'\n{name} - Query: \"{query}\"')
        for i, doc in enumerate(results[:3]):
            preview = doc.page_content[:80] + '...'
            print(f'  {i+1}. {preview}')
        return results

    test_queries = [
        'sku-90876 specifications?',
        'E_CAM_Refused error',
        'admin settings?'
    ]

    for query in test_queries:
        vector_results = test_query(query, 'VECTOR', vector_retriever)
        bm25_results = test_query(query, 'BM25', bm25_retriever)


if __name__ == '__main__' :
    hybrid_search()