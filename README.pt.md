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

O **DocFlow AI** é uma plataforma de processamento de documentos educacionais baseada em IA, projetada para auxiliar professores e instituições de ensino por meio de análise inteligente de documentos, processamento semântico, embeddings e futura recuperação contextual baseada em RAG.

## ✅ Funcionalidades Atuais

- Upload de PDF
- Upload de DOCX
- Upload de imagem
- Extração OCR com Tesseract
- Divisão semântica (Semantic chunking)
- Estruturação com Gemini AI
- Geração de embeddings
- Persistência em PostgreSQL
- Suporte a pgvector
- Testes unitários e de integração
- Pipeline de CI/CD


## 🧠 Core
O projeto foca em transformar documentos pedagógicos em dados educacionais estruturados, insights, métricas e conhecimento semântico que possam apoiar:

- geração de planos de aula
- atividades personalizadas
- avaliações inteligentes
- recomendações pedagógicas
- análise de dados educacionais (educational analytics)
- assistência ao professor baseada em IA



## 🧱 Arquitetura do Sistema

```text
Upload
   ↓
OCR / Parsing
   ↓
Estruturação por IA
   ↓
Divisão (Chunking)
   ↓
Embeddings
   ↓
Banco Vetorial
   ↓
Futuro Pipeline RAG
```

## 🧠 Futura Arquitetura RAG
O sistema atual já gera embeddings semânticos e dados pedagógicos fragmentados.

O próximo passo é a implementação de:

- recuperação semântica
- busca contextual
- recomendações pedagógicas
- geração de planos de aula
- assistente inteligente para o professor

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

### Criar o .env

```env
DATABASE_URL=
DATABASE_TEST_URL=
GEMINI_API_KEY=
```

### Executar o Banco de Dados (se aplicável)
```bash
python -m app.db.create_tables 
```

### Executar o projeto

```bash
uvicorn app.main:app --reload
```

### API em Execução
```bash
http://localhost:8000/docs
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