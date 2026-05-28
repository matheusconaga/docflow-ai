<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/Lang-English-blue?style=for-the-badge" alt="English"></a>
  <a href="README.pt.md"><img src="https://img.shields.io/badge/Lang-Português-green?style=for-the-badge" alt="Português"></a>
</p>

<h1 align="center">🧠 DocFlow AI</h1>

<p align="center">
Pipeline inteligente de processamento de documentos pedagógicos utilizando IA, OCR, embeddings e busca semântica.
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

## 📌 Sobre o Projeto

O **DocFlow AI** é uma plataforma de processamento de documentos educacionais baseada em IA, projetada para auxiliar professores e instituições de ensino por meio de análise inteligente de documentos, processamento semântico, embeddings e recuperação contextual baseada em RAG.

## ✅ Funcionalidades

- Upload de PDF, DOCX e imagem
- Extração OCR com Tesseract
- Estruturação com Gemini AI (matéria, nível, habilidades, metodologias)
- Chunking semântico (6 tipos pedagógicos)
- Geração de embeddings com `gemini-embedding-001`
- Armazenamento vetorial com pgvector
- Pipeline RAG — recuperação semântica + geração com Gemini
- Persistência em PostgreSQL
- Testes unitários e de integração
- Pipeline de CI/CD

## 🧱 Arquitetura do Sistema

```text
Upload
   ↓
OCR / Parsing
   ↓
Estruturação por IA (Gemini)
   ↓
Chunking Semântico
   ↓
Geração de Embeddings
   ↓
Armazenamento pgvector
   ↓
Pipeline RAG (recuperar → gerar)
```

## 🔍 Pipeline RAG

Cada documento é dividido em 6 tipos de chunks semânticos:

| Tipo | Descrição |
|---|---|
| `lesson_plan` | Matéria, nível, conteúdos, habilidades, metodologias |
| `activity` | Atividades práticas derivadas do documento |
| `assessment` | Estratégias de avaliação |
| `bncc` | Alinhamento à Base Nacional Curricular |
| `recommendation` | Recomendações pedagógicas |
| `insight` | Insights de aprendizagem |

**Fluxo de consulta:**
1. Pergunta do usuário → embedded com `gemini-embedding-001`
2. Busca por similaridade cosseno no pgvector → top-k chunks relevantes
3. Chunks recuperados → injetados como contexto no prompt do Gemini
4. Gemini gera resposta baseada apenas no contexto dos documentos

**Endpoints RAG:**

```
POST /rag/query   → pipeline completo: retorna resposta + chunks de origem
POST /rag/search  → só busca semântica: retorna chunks rankeados
```

Exemplo:
```json
POST /rag/query
{
  "query": "Como planejar uma aula engajante sobre frações?",
  "top_k": 5,
  "chunk_type": "lesson_plan"
}
```

## 🐳 Executando com Docker

### Clonar o repositório

```bash
git clone https://github.com/matheusconaga/docflow-ai.git

cd docflow-ai
```

### Criar o .env

```env
DATABASE_URL=
DATABASE_TEST_URL=
GEMINI_API_KEY=
```

### Executar o projeto

```bash
docker compose up --build
```

### API em Execução
```bash
http://localhost:8000/docs
```

## 💻 Executando sem Docker

### Clonar o repositório

```bash
git clone https://github.com/matheusconaga/docflow-ai.git

cd docflow-ai
```

### Criar o ambiente virtual
```bash
python -m venv venv
```

### Ativar o ambiente virtual
```bash
Windows (PowerShell)

.\venv\Scripts\Activate
```
```bash
Linux / Mac

source venv/bin/activate
```

### Instalar dependências
```bash
pip install -r requirements.txt
```

### Instalar pgvector e Tesseract (macOS)
```bash
brew install tesseract tesseract-lang

# Compilar pgvector para sua versão do PostgreSQL
cd /tmp && git clone --branch v0.8.2 https://github.com/pgvector/pgvector.git
cd pgvector
PG_CONFIG=/opt/homebrew/opt/postgresql@14/bin/pg_config make
sudo PG_CONFIG=/opt/homebrew/opt/postgresql@14/bin/pg_config make install
```

### Criar o .env

```env
DATABASE_URL=
DATABASE_TEST_URL=
GEMINI_API_KEY=
```

### Executar migrações do banco
```bash
# Cria as tabelas e habilita a extensão pgvector
python -m app.db.create_tables

# Converte a coluna embedding de JSON para vector(3072)
python -m app.db.migrations.add_pgvector
```

### Executar o projeto

```bash
uvicorn app.main:app --reload
```

### API em Execução
```bash
http://localhost:8000/docs
```

### Pipeline de processamento de documentos

```
POST /documents/upload
POST /documents/{id}/extract
POST /documents/{id}/structure
POST /documents/{id}/chunk
POST /documents/{id}/embeddings   ← obrigatório antes de usar o RAG
```

## 🧪 Testes
O projeto contém:

- testes unitários
- testes de integração
- testes de rotas da API
- testes de embedding
- testes de OCR

Cobertura gerada com:

- pytest
- pytest-cov

## Para Executar os Testes
```bash
pytest --cov=app
```

## ⚙️ CI/CD
Pipeline automatizado com GitHub Actions:

- lint
- testes
- docker build
- deploy
- health check

<p>
  <img src="https://github.com/matheusconaga/docflow-ai/blob/main/assets/pipeline.png?raw=true" width="800"/>
</p>

## 📄 Licença
Copyright © 2026 Matheus Lula.

Todos os direitos reservados.

Este projeto está disponível apenas para fins de portfólio e educacionais.

O uso comercial, distribuição ou reprodução não autorizada é proibido.

## 👨‍💻 Autor

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