from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
import os
import tempfile

from langchain.chat_models import init_chat_model 

load_dotenv()

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
MODEL = os.getenv("MODEL")

embeddings_model = OllamaEmbeddings(model = EMBEDDING_MODEL)


def create_kb():
    splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50)
    doc = Document(page_content = "This document is about Iphones.",
                   metadata = {"source": "sample_doc.txt"})

    chunks = splitter.split_documents([doc])

    #create vector store

    vector_store = Chroma.from_documents(
        documents = chunks,
        embedding = embeddings_model,
        persist_directory = tempfile.mkdtemp()
    )

    return vector_store

def demo_basic_rag():

    vector_store = create_kb()
    retriever = vector_store.as_retriever(search_type = "similarity", search_kwargs = {"k":2})

    llm = ChatOllama(
        model = MODEL,
        temperature = 0.1,
        streaming = False
    )

    #RAG prompt template
    prompt = ChatPromptTemplate.from_template(
        """
        Answer the following only based on context:
        {context}
        Question: {question}

        Answer;
        If you don't know the answer, Just say you don't know."""
    )

    def format_docs(docs) :
        return "\n\n".join([doc.page_content for doc in docs])

    rag_chain = (
        {
            "context" : retriever | format_docs,
            "question" : RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    question = "What is the context about?"

    answer = rag_chain.invoke(question)
    print(f"Question: {question}")
    print(f"Answer: {answer}")


if __name__ == "__main__":
    demo_basic_rag()