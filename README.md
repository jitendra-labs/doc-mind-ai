# 🏥  DocMind AI -  (Intelligent Medical Document Platform)

> Production-grade Retrieval-Augmented Generation (RAG) platform for medical document intelligence, semantic search, and AI-powered clinical question answering.

---

## 🚀 Overview

The Intelligent Medical Document Platform transforms unstructured healthcare documents into a searchable knowledge system using modern AI technologies.

Users can upload medical PDFs such as:

- Discharge Summaries
- Lab Reports
- Radiology Reports
- Consultation Notes
- Clinical Documentation

The platform automatically extracts text, generates embeddings, stores vectors in PostgreSQL with pgvector, and enables natural language question answering with source citations.

Unlike traditional search systems, answers are grounded entirely in uploaded documents, reducing hallucinations and improving trustworthiness.

---

## 🎯 Problem Statement

Healthcare professionals often spend significant time manually reviewing large volumes of clinical documentation.

Important information is frequently buried across:

- Hundreds of pages
- Multiple report types
- Different patient encounters
- Historical medical records

This platform solves that problem by providing:

✅ Semantic Search

✅ AI-Powered Question Answering

✅ Source Attribution

✅ Fast Information Retrieval

✅ Document Intelligence

---

# 🏗 Architecture

```text
                        ┌──────────────────┐
                        │      User        │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │     FastAPI      │
                        └────────┬─────────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           ▼                     ▼                     ▼

 ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
 │ Upload Document │   │ Ask Questions   │   │ Metadata APIs   │
 └────────┬────────┘   └────────┬────────┘   └─────────────────┘
          │                     │
          ▼                     ▼

 ┌─────────────────────────────────────────────┐
 │            Ingestion Pipeline               │
 └─────────────────────────────────────────────┘
          │
          ▼

 ┌─────────────────┐
 │ PDF Extraction  │
 └────────┬────────┘
          ▼

 ┌─────────────────┐
 │ Text Chunking   │
 └────────┬────────┘
          ▼

 ┌─────────────────┐
 │ Embeddings      │
 └────────┬────────┘
          ▼

 ┌─────────────────────────────┐
 │ PostgreSQL + pgvector       │
 └─────────────┬───────────────┘
               │
               ▼

      Semantic Vector Search

               │
               ▼

       Retrieved Context

               │
               ▼

            Ollama LLM

               │
               ▼

        Grounded Response
```

---

## Prerequisites

- Docker + Docker Compose
- ~8-16GB free RAM (for the Ollama model)
- A modern browser

---

# ✨ Key Features

## 📄 Document Ingestion

Upload PDF documents and automatically:

- Extract text
- Generate embeddings
- Create searchable chunks
- Store vectors in PostgreSQL

---

## 🤖 AI-Powered Question Answering

Ask questions using natural language:

```text
What disease was Arjun Mehta diagnosed with?

Which patient underwent appendectomy?

What were David Thomas's cardiac biomarker results?
```

---

## 🔍 Semantic Search

Uses embeddings and vector similarity search to find relevant information even when exact keywords are not present.

---

## 📌 Source Citations

Every response includes source references.

Example:

```text
Answer

Acute exacerbation of chronic obstructive pulmonary disease (COPD), GOLD stage III.

Sources

• discharge_summary_arjun_mehta.pdf (Page 1)

Confidence: High
```

---

## 🛡 Hallucination Prevention

The system:

- Uses only retrieved document context
- Never guesses missing information
- Clearly indicates when information is unavailable
- Provides citations for every answer

---

## 🧠 RAG Pipeline

### 1. Upload Document

```text
PDF Upload
```

↓

### 2. Extract Text

```text
PDF → Raw Text
```

↓

### 3. Chunk Content

```text
Raw Text → Chunks
```

↓

### 4. Generate Embeddings

```text
Chunk → Vector Embedding
```

↓

### 5. Store in PostgreSQL

```text
Chunk + Metadata + Embedding
```

↓

### 6. Retrieve Relevant Context

```text
Question → Similarity Search
```

↓

### 7. Inject Context into Prompt

```text
Question + Retrieved Chunks
```

↓

### 8. Generate Grounded Answer

```text
LLM Response + Citations
```

---

# 🛠 Technology Stack

## Backend

- Python 3.12+
- FastAPI
- SQLAlchemy
- Alembic

## Database

- PostgreSQL
- pgvector

## AI / Machine Learning

- Ollama
- Sentence Transformers
- Retrieval-Augmented Generation (RAG)

## Document Processing

- pdfplumber
- OCR-ready architecture

## Infrastructure

- Docker
- Docker Compose

---

# 🗄 Database Design

## Documents

Stores uploaded document metadata.

| Field | Description |
|---------|-------------|
| id | UUID |
| filename | Document name |
| document_type | Report category |
| uploaded_at | Upload timestamp |

---

## Chunks

Stores searchable text fragments.

| Field | Description |
|---------|-------------|
| id | UUID |
| document_id | Parent document |
| page_number | Source page |
| chunk_text | Extracted text |
| embedding | Vector representation |

---

# 📡 API Examples

## Upload Document

```http
POST /documents/upload
```

---

## Ask Question

```http
POST /chat/ask
```

Request:

```json
{
  "question": "What disease does Arjun Mehta have?"
}
```

Response:

```json
{
  "answer": "Acute exacerbation of chronic obstructive pulmonary disease (COPD), GOLD stage III.",
  "confidence": "high",
  "sources": [
    {
      "file": "discharge_summary_arjun_mehta.pdf",
      "page": 1
    }
  ]
}
```

---
## Run migration inside docker container

```bash
docker compose exec backend alembic upgrade head
```

---

# 🔒 Reliability & Trust

### Grounded Responses

Answers are generated exclusively from retrieved document context.

### Explainable AI

Every answer includes source references.

### Auditable Results

Responses can always be traced back to original documents and pages.

### Domain-Specific Retrieval

Designed specifically for medical document intelligence workflows.

---

# 📈 Future Enhancements

## Retrieval

- Hybrid Search (Vector + Full Text)
- Metadata Filtering
- Re-ranking Pipelines

## AI

- Query Rewriting
- Multi-document Reasoning
- Agentic Retrieval

## Medical Intelligence

- Medication Extraction
- Clinical Timeline Generation
- ICD Code Detection
- Patient Summarization

## Enterprise

- Multi-Tenant Architecture
- RBAC Authorization
- Audit Logging
- SSO Integration

---

# 🎓 Learning Objectives

This project demonstrates practical implementation of:

### AI Engineering

- Retrieval-Augmented Generation (RAG)
- Embeddings
- Vector Databases
- Prompt Engineering
- Context Injection

### Backend Engineering

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

### Production Architecture

- Document Ingestion Pipelines
- Vector Search Systems
- AI Service Integration
- Healthcare Document Intelligence

---

# 💡 Why This Project Matters

Modern AI applications increasingly rely on organizational knowledge rather than standalone language models.

This project demonstrates how Large Language Models can be combined with:

- Vector Databases
- Embedding Models
- Retrieval Systems
- Domain-Specific Documents

to build trustworthy, explainable, and production-ready AI solutions.

The same architecture can be extended to:

- Healthcare Intelligence
- Legal Document Search
- Financial Research
- Enterprise Knowledge Management
- Compliance Automation

---

<img width="1918" height="1017" alt="Screenshot from 2026-07-16 11-31-30" src="https://github.com/user-attachments/assets/e8a51334-d970-493e-95c0-3a95c418fb40" />



## 👨‍💻 Author

Built as a practical exploration of modern AI Engineering, Retrieval-Augmented Generation (RAG), Vector Search, and Medical Document Intelligence using Python and FastAPI.

---

⭐ If you found this project interesting, consider giving it a star.
