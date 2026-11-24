from langchain_core.prompts import ChatPromptTemplate
from starlette.concurrency import run_in_threadpool

from app.services.llm_service import get_llm
from app.services.retrieval_service import StepCallback, pipeline_step, retrieve_documents

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


def _llm_name(llm) -> str:
    return getattr(llm, "model_name", None) or getattr(llm, "model", None) or type(llm).__name__


async def run_rag_pipeline(question: str, retrieval_type: str = "similarity", k: int = 3, use_reranker: bool = False, on_step: StepCallback = None):
    """Retrieve → generate. Reports each stage to `on_step` and returns the retrieved chunks as well."""

    # Retrieval is synchronous (Chroma, BM25, cross-encoder): keep it off the event loop.
    documents = await run_in_threadpool(
        retrieve_documents,
        question,
        k,
        retrieval_type,
        use_reranker,
        on_step = on_step
    )

    context = "\n\n".join(
        doc.page_content for doc in documents
    )

    llm = get_llm()
    chain = prompt | llm

    with pipeline_step(on_step, "generate", f"Generating answer ({_llm_name(llm)})") as info:
        response = await chain.ainvoke({
            "context": context,
            "question" : question
        })
        info["detail"] = f"{len(documents)} chunks as context · {len(context):,} chars"

    sources = [
        {
            "source" : doc.metadata.get("filename") or doc.metadata.get("source"),
            "page" : doc.metadata.get("page") + 1
                if doc.metadata.get("page") is not None
                else None
        }
        for doc in documents
    ]

    chunks = [
        {
            "rank": rank,
            "content": doc.page_content,
            "metadata": doc.metadata
        }
        for rank, doc in enumerate(documents, start = 1)
    ]

    return {
        "response" : response.content,
        "sources" : sources,
        "chunks": chunks
    }


async def generate_rag_response(question: str, retrieval_type: str = "similarity", k: int = 3, use_reranker: bool = False):
    result = await run_rag_pipeline(question, retrieval_type, k, use_reranker)

    return {
        "response" : result["response"],
        "sources" : result["sources"]
    }
