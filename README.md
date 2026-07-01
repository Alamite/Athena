# Athena

A production-oriented Retrieval-Augmented Generation (RAG) system that answers questions using a custom document corpus and provides evidence-backed responses with verifiable citations.

## Overview

Large Language Models can generate convincing answers, but they cannot always guarantee accuracy. The goal of this project is to build a system that retrieves relevant information from a knowledge base and grounds every answer in actual source documents.

The project is being built incrementally with a strong focus on retrieval quality, citation accuracy, evaluation, and production readiness.

---

## Project Goals

* Ingest documents from multiple sources
* Chunk documents intelligently
* Generate vector embeddings
* Store embeddings in a vector database
* Retrieve relevant context using semantic search
* Generate answers using retrieved context
* Provide verifiable citations
* Prevent unsupported answers
* Evaluate retrieval and generation quality
* Support production-grade retrieval architectures

---

## Current Architecture

```text
Documents
    ↓
Loader
    ↓
Chunker
    ↓
Chunks
    ↓
Embeddings
    ↓
ChromaDB
    ↓
Semantic Search
    ↓
Retriever
    ↓
Distance Filtering
    ↓
Context Builder
    ↓
LLM
    ↓
Answer + Citations
```

---

## Repository Structure

```text
ask-my-db/

├── app/
│
├── configs/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── embeddings/
│   └── embedder.py
│
├── evaluation/
│
├── generation/
│   ├── answer_generator.py
│   └── citations.py
│
├── ingestion/
│   ├── chunker.py
│   ├── loaders.py
│   ├── pipeline.py
│   └── schema.py
│
├── retrieval/
│   ├── context_builder.py
│   ├── filters.py
│   └── retriever.py
│
├── scripts/
│   ├── ask.py
│   ├── build_index.py
│   ├── ingest.py
│   └── search.py
│
├── tests/
│
├── vectorstore/
│   └── chroma_store.py
│
└── README.md
```

---

# Phase 1: Foundations

## 1. Document Ingestion

The ingestion pipeline loads raw documents and converts them into structured chunks.

### Supported Input Types (Current)

* Markdown (.md)

### Planned

* PDF
* HTML
* Web Pages

### Loader

Responsible for reading raw documents and extracting text content.

Example Output:

```json
{
  "document_name": "langgraph_memory",
  "source": "data/raw/langgraph_memory.md",
  "content": "..."
}
```

---

## 2. Chunking

Documents are split into smaller pieces before embedding.

### Why Chunking?

Embedding entire documents leads to:

* Poor retrieval quality
* Increased cost
* Larger context windows

Chunking allows retrieval at a much finer granularity.

### Current Strategy

Using:

```python
RecursiveCharacterTextSplitter
```

Configuration:

```python
chunk_size = 700
chunk_overlap = 100
```

Benefits:

* Preserves context across chunk boundaries
* Reduces information loss
* Produces retrieval-friendly chunks

---

## 3. Chunk Schema

Each chunk contains metadata required for retrieval and citations.

Example:

```json
{
  "id": "uuid",
  "document_name": "langgraph_memory",
  "source": "data/raw/langgraph_memory.md",
  "chunk_index": 0,
  "content": "...",
  "metadata": {}
}
```

---

## 4. Embeddings

Chunks are converted into vector representations.

### Current Model

```text
BAAI/bge-small-en-v1.5
```

Why?

* Strong retrieval performance
* Lightweight
* Open source
* Fast inference

---

## 5. Vector Store

### Current Choice

ChromaDB

Features:

* Local persistence
* Easy setup
* Fast similarity search
* Great for experimentation

Stored Data:

* Chunk ID
* Document Content
* Metadata
* Embeddings

---

## 6. Semantic Search

A query is converted into an embedding and compared against stored vectors.

Workflow:

```text
Question
    ↓
Embedding
    ↓
Vector Search
    ↓
Top-K Results
```

Example:

```text
Question:
How does LangGraph persistence work?

Retrieved Chunk:
LangGraph supports persistence through checkpointing.
```

---

## 7. Retriever Layer

A dedicated retriever abstraction separates retrieval logic from generation logic.

Responsibilities:

* Query embedding
* Vector search
* Result formatting
* Retrieval orchestration

Output:

```python
[
    {
        "content": "...",
        "metadata": {...},
        "distance": 0.23
    }
]
```

---

## 8. Distance Filtering

Not every retrieved chunk should be trusted.

The system filters low-quality matches using similarity thresholds.

Example:

```python
MAX_DISTANCE = 0.8
```

If no chunks meet the threshold:

```text
I cannot answer based on the retrieved documents.
```

This prevents unsupported answers and reduces hallucinations.

---

## 9. Context Builder

Retrieved chunks are transformed into a structured context block for the LLM.

Example:

```text
[Document: langgraph_memory]
[Chunk: 0]

LangGraph supports persistence through checkpointing.

----------------------------------------

[Document: state_management]
[Chunk: 2]

State can be stored externally.
```

---

## 10. Answer Generation

The LLM receives:

* User Question
* Retrieved Context

Prompt Rules:

* Use only supplied context
* Do not invent information
* Refuse unsupported answers

Current Failure Response:

```text
I cannot answer based on the retrieved documents.
```

---

## 11. Citation Generation

One of the most important parts of the project.

### Design Decision

The LLM does NOT generate citations.

Instead:

```text
Retriever
    ↓
Chunk Metadata
    ↓
Citation Generator
```

This guarantees citations correspond to actual retrieved chunks.

Example:

```text
Answer:

LangGraph persistence is implemented through checkpointing.

Citations:

[1] langgraph_memory (chunk 0)
[2] state_management (chunk 2)
```

---

# Running the Project

## 1. Install Dependencies

```bash
pip install chromadb
pip install sentence-transformers
pip install langchain-text-splitters
pip install openai
```

---

## 2. Ingest Documents

```bash
python scripts/ingest.py
```

Output:

```text
Generated 42 chunks
Saved to data/processed/chunks.json
```

---

## 3. Build Vector Index

```bash
python scripts/build_index.py
```

Output:

```text
Generating embeddings...
Generated 42 embeddings
Indexing complete
```

---

## 4. Test Semantic Search

```bash
python scripts/search.py
```

Example:

```text
Question:
How does LangGraph persistence work?
```

---

## 5. Ask Questions

```bash
python scripts/ask.py
```

Example:

```text
Question:
How does LangGraph persistence work?
```

Output:

```text
ANSWER

LangGraph persistence is implemented through checkpointing.

CITATIONS

[1] langgraph_memory (chunk 0)
```

---

# Planned Improvements

## Phase 2 - Production Retrieval

### Hybrid Search

Combine:

* BM25
* Vector Search

Architecture:

```text
BM25
   +
Vector Search
   ↓
Fusion
```

Benefits:

* Better keyword matching
* Better semantic understanding
* Improved recall

---

### Cross Encoder Reranking

Model:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

Workflow:

```text
Top 20 Results
      ↓
Cross Encoder
      ↓
Top 5 Results
```

Benefits:

* Improved precision
* Better ranking quality

---

### Citation Enforcement

The system should explicitly refuse to answer when retrieved evidence is insufficient.

---

## Phase 3 - Evaluation & Production Readiness

### Golden Dataset

Curated QA pairs for regression testing.

Target:

```text
50 - 200 verified questions
```

---

### Evaluation Metrics

Using RAGAS:

* Faithfulness
* Context Precision
* Context Recall
* Answer Relevancy

---

### Continuous Integration

Every pull request will trigger:

```text
Evaluation Run
      ↓
Metric Validation
      ↓
Pass / Fail
```

The build should fail if retrieval quality drops below a defined threshold.

---

## Future Enhancements

* FastAPI Backend
* React Frontend
* Streaming Responses
* Multi-document Corpora
* Knowledge Graph Retrieval
* MCP Integration
* Retrieval Analytics Dashboard
* Feedback Collection
* Agent Integration
* Multi-modal RAG

---

## Key Engineering Principles

This project prioritizes:

* Grounded generation
* Evidence-backed answers
* Separation of retrieval and generation
* Explicit citation handling
* Evaluation-driven development
* Production-oriented architecture

The objective is not simply to build a chatbot, but to build a trustworthy retrieval system that can be deployed and maintained in production environments.
