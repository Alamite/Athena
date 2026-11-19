from langchain_core.prompts import ChatPromptTemplate

from app.services.llm_service import get_llm
from app.services.retrieval_service import retrieve_documents

prompt = ChatPromptTemplate.from_template(
    """
    Answer the question using ONLY the provided context.

    If the answer is not available in the context,
    say that you don't have enough information.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
)

async def generate_rag_response(question: str, retrieval_type: str = "similarity", k: int = 3, use_reranker: bool = False):
    documents = retrieve_documents(question, k, retrieval_type, use_reranker)

    context = "\n\n".join(
        doc.page_content for doc in documents
    )

    chain = prompt | get_llm()

    response = await chain.ainvoke({
        "context": context,
        "question" : question
    })

    sources = [
        {
            "source" : doc.metadata.get("filename") or doc.metadata.get("source"),
            "page" : doc.metadata.get("page") + 1
                if doc.metadata.get("page") is not None
                else None
        }
        for doc in documents
    ]

    return {
        "response" : response.content,
        "sources" : sources
    }