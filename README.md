# DOCFLOW-IA

Sistema inteligente para análise pedagógica de documentos utilizando IA, processamento semântico, embeddings e RAG.

O objetivo do projeto é transformar documentos educacionais em informações estruturadas, métricas e insights pedagógicos que poderão futuramente servir como base para:

- geração de planos de aula
- criação de atividades
- elaboração de avaliações
- análise de desempenho
- recomendações pedagógicas
- assistente inteligente para professores

---

# Status do Projeto

## 🚧 Em desenvolvimento ativo.

Atualmente o foco do projeto está na construção do núcleo da plataforma:

```text
Documento → IA → Estruturação → Métricas → Insights
```

A arquitetura está sendo desenvolvida de forma escalável para suportar futuras funcionalidades de RAG, geração de conteúdo e automações pedagógicas.

---

# Objetivo do MVP

O MVP inicial possui foco em:

- upload de documentos
- extração de texto
- estruturação inteligente
- análise pedagógica
- geração de métricas
- geração de insights

---

# Pipeline de Desenvolvimento

## Etapas planejadas

### 1. Upload
Recebimento de arquivos:
- PDF
- DOCX
- imagens

---

### 2. Parsing
Extração de texto utilizando:
- PyMuPDF
- pdfplumber
- OCR (Tesseract)

---

### 3. Estruturação IA
Transformação do conteúdo em dados estruturados:
- temas
- habilidades
- competências
- cronogramas
- dificuldade
- carga horária

---

### 4. Persistência
Armazenamento:
- documentos
- texto extraído
- análises
- embeddings

---

### 5. Chunking
Divisão semântica do conteúdo.

---

### 6. Embeddings
Transformação textual em vetores semânticos.

---

### 7. Banco Vetorial
Armazenamento vetorial utilizando:
- pgvector
- PostgreSQL

---

### 8. Métricas
Geração de métricas pedagógicas:
- complexidade
- densidade pedagógica
- tempo estimado
- risco de atraso

---

### 9. Insights
Geração de insights inteligentes:
- excesso de conteúdo
- distribuição inadequada
- falta de revisão
- sugestões pedagógicas

---

### 10. RAG
Recuperação contextual baseada nos documentos processados.

---

### 11. Geração de Conteúdo
Geração automática de:
- planos de aula
- atividades
- avaliações
- feedbacks

---

### 12. CI/CD
Pipeline automatizado:
- testes
- build
- deploy
- integração contínua

---

# Stack Inicial

## Backend
- Python
- FastAPI
- SQLAlchemy

## Banco de Dados
- PostgreSQL
- Neon

## IA
- OpenAI
- Embeddings
- RAG

## Processamento
- Celery
- OCR
- Chunking

## Infraestrutura
- Docker
- GitHub Actions

---

# Estrutura Inicial

```bash
app/
├── api/
├── ai/
├── core/
├── models/
├── schemas/
├── services/
├── workers/
└── storage/
```

---

# Arquitetura

O projeto segue uma arquitetura modular baseada em separação de responsabilidades:

```text
API → Services → Pipeline → AI Modules → Database
```

Isso permite:
- escalabilidade
- manutenção simplificada
- evolução gradual do MVP
- desacoplamento entre IA e API

---

# Roadmap

## Curto prazo
- Upload de documentos
- Parsing
- Estruturação IA
- Métricas básicas

## Médio prazo
- Embeddings
- Busca vetorial
- RAG

## Longo prazo
- Geração de conteúdo pedagógico
- Assistente inteligente para professores
- Personalização por turma/aluno
- Plataforma educacional completa

---

# Observações

Este projeto encontra-se em fase inicial de desenvolvimento e sua arquitetura poderá evoluir conforme validações do MVP e necessidades futuras.