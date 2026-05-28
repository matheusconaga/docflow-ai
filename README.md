<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/Lang-English-blue?style=for-the-badge" alt="English"></a>
  <a href="README.pt.md"><img src="https://img.shields.io/badge/Lang-Português-green?style=for-the-badge" alt="Português"></a>
</p>

<h1 align="center">🧠 DocFlow AI</h1>

<p align="center">
Intelligent pedagogical document processing pipeline using AI, OCR, embeddings and semantic search.
</p>

<p align="center">
  <img src="https://github.com/matheusconaga/docflow-ai/blob/main/assets/docflow.png?raw=true" width="800"/>
</p>

<p align="center">

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white"/>
<img src="https://img.shields.io/badge/pgvector-336791?style=for-the-badge&logo=postgresql&logoColor=white"/>
<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
<img src="https://img.shields.io/badge/Gemini_AI-4285F4?style=for-the-badge&logo=google&logoColor=white"/>
<img src="https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white"/>
<img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white"/>

</p>

<p align="center">
  <a href="https://docflow-ai-lj3a.onrender.com/" target="_blank">
    <img src="https://img.shields.io/badge/🌐%20Live%20Demo-000000?style=for-the-badge"/>
  </a>
</p>

## 📌 About the Project

**DocFlow AI** is an AI-powered educational document processing platform designed to assist teachers and educational institutions through intelligent document analysis, semantic processing, embeddings, and RAG-based contextual retrieval.

## ✅ Features

- PDF, DOCX and image upload
- OCR extraction with Tesseract
- Gemini AI structuring (subject, level, skills, methodologies)
- Semantic chunking (6 pedagogical types)
- Embedding generation with `gemini-embedding-001`
- Vector storage with pgvector
- RAG pipeline — semantic retrieval + Gemini generation
- PostgreSQL persistence
- Unit and integration tests
- CI/CD pipeline

## 🧱 System Architecture

```text
Upload
   ↓
OCR / Parsing
   ↓
AI Structuring (Gemini)
   ↓
Semantic Chunking
   ↓
Embedding Generation
   ↓
pgvector Storage
   ↓
RAG Pipeline (retrieve → generate)
```

## 🔍 RAG Pipeline

Each document is split into 6 semantic chunk types:

| Type | Description |
|---|---|
| `lesson_plan` | Subject, level, contents, skills, methodologies |
| `activity` | Practical activities derived from the document |
| `assessment` | Assessment strategies |
| `bncc` | Brazilian national curriculum alignment |
| `recommendation` | Pedagogical recommendations |
| `insight` | Learning insights |

**Query flow:**
1. User question → embedded with `gemini-embedding-001`
2. pgvector cosine similarity search → top-k relevant chunks
3. Retrieved chunks → injected as context into Gemini prompt
4. Gemini generates a grounded answer based only on document context

**RAG endpoints:**

```
POST /rag/query   → full pipeline: returns answer + source chunks
POST /rag/search  → semantic search only: returns ranked chunks
```

Example:
```json
POST /rag/query
{
  "query": "How to plan an engaging lesson on fractions?",
  "top_k": 5,
  "chunk_type": "lesson_plan"
}
```

## 🐳 Running with Docker

### Clone repository

```bash
git clone https://github.com/matheusconaga/docflow-ai.git

cd docflow-ai
```

### Create .env

```env
DATABASE_URL=
DATABASE_TEST_URL=
GEMINI_API_KEY=
```

### Run project

```bash
docker compose up --build
```

### API is Running
```bash
http://localhost:8000/docs
```

## 💻 Running without Docker

### Clone repository

```bash
git clone https://github.com/matheusconaga/docflow-ai.git

cd docflow-ai
```

### Create virtual environment
```bash
python -m venv venv
```

### Activate virtual environment
```bash
Windows (PowerShell)

.\venv\Scripts\Activate
```
```bash
Linux / Mac

source venv/bin/activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Install pgvector (macOS)
```bash
brew install tesseract tesseract-lang

# Build pgvector for your PostgreSQL version
cd /tmp && git clone --branch v0.8.2 https://github.com/pgvector/pgvector.git
cd pgvector
PG_CONFIG=/opt/homebrew/opt/postgresql@14/bin/pg_config make
sudo PG_CONFIG=/opt/homebrew/opt/postgresql@14/bin/pg_config make install
```

### Create .env

```env
DATABASE_URL=
DATABASE_TEST_URL=
GEMINI_API_KEY=
```

### Run database migration
```bash
# Creates tables and enables pgvector extension
python -m app.db.create_tables

# Converts embedding column from JSON to vector(3072)
python -m app.db.migrations.add_pgvector
```

### Run project

```bash
uvicorn app.main:app --reload
```

### API is Running
```bash
http://localhost:8000/docs
```

### Document processing pipeline

```
POST /documents/upload
POST /documents/{id}/extract
POST /documents/{id}/structure
POST /documents/{id}/chunk
POST /documents/{id}/embeddings   ← required before using RAG
```

## 🧪 Tests
The project contains:

- unit tests
- integration tests
- API route tests
- embedding tests
- OCR tests

Coverage generated with:

- pytest
- pytest-cov

## For Run Tests
```bash
pytest --cov=app
```

## ⚙️ CI/CD
Automated pipeline with GitHub Actions:

- lint
- tests
- docker build
- deployment
- health check

<p>
  <img src="https://github.com/matheusconaga/docflow-ai/blob/main/assets/pipeline.png?raw=true" width="800"/>
</p>

## 📄 License

Copyright © 2026 Matheus Lula.

All rights reserved.

This project is available for portfolio and educational purposes only.

Unauthorized commercial use, distribution, or reproduction is prohibited.

## 👨‍💻 Author

<p align="center">
  <img src="https://avatars.githubusercontent.com/matheusconaga" width="110px;" style="border-radius:50%;" />
</p>

<h3 align="center">Matheus Lula</h3>

<p align="center">
Full-Stack Developer • React • Flutter • FastAPI • AI & Automation</p>

<div align="center">
<a href="mailto:matheusphillip170@gmail.com"><img src="https://img.shields.io/badge/Gmail-FF0000?style=for-the-badge&logo=gmail&logoColor=white"/></a>
<a href="https://www.linkedin.com/in/matheusconaga/"><img src="https://img.shields.io/badge/💼%20LinkedIn-0e76a8?style=for-the-badge&logo=linkedin"/></a>
<a href="https://portifoliomatheuslula.onrender.com/"><img src="https://img.shields.io/badge/Portfólio-000000?style=for-the-badge&logo=render&logoColor=white"/></a>
</div>