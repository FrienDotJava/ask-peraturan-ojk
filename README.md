# Ask Peraturan OJK

A RAG (Retrieval-Augmented Generation) application that answers questions about OJK (Otoritas Jasa Keuangan) regulations in Bahasa Indonesia. The system retrieves relevant content from official OJK regulatory documents and generates grounded, cited answers using a large language model.

## Demo

| Application | URL | Type |
|------------|-----|------|
| **API** | [ask-peraturan-ojk-backend.onrender.com](https://ask-peraturan-ojk-backend.onrender.com) | FastAPI |
| **Model Inference App** | [ask-peraturan-ojk.vercel.app](https://ask-peraturan-ojk.vercel.app/) | Next.js |

---

## Why This Project

OJK regulations are dense, spread across dozens of POJK documents, and difficult to navigate for founders, fintech operators, and compliance teams. This tool lets users ask questions in plain Bahasa Indonesia and get direct answers with source citations, without reading through entire regulation PDFs.

---

## Architecture

```
User Question
      |
      v
 Hybrid Retriever  <-- BM25 (keyword) + ChromaDB (semantic)
      |
      v
  Cross-Encoder Reranker  <-- selects top 3 most relevant chunks
      |
      v
  Document Grader  <-- LLM decides if local docs are sufficient
      |
      v
  Web Search (Tavily)  <-- fallback if local docs are insufficient
      |
      v
  Answer Generator  <-- Mistral Medium 3 with strict grounding prompt
      |
      v
  Streaming Response  <-- tokens streamed via SSE to Next.js frontend
```

The pipeline is orchestrated with LangGraph as an agentic workflow. Each step is a separate node with a defined state, making the flow easy to extend and debug.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js (TypeScript) |
| Backend | FastAPI |
| Orchestration | LangChain + LangGraph |
| LLM | Mistral Medium 3 |
| Embeddings | Cohere embed-multilingual-v3.0 |
| Vector Store | ChromaDB |
| Retrieval | BM25 + Semantic (Ensemble) + Cross Encoder Reranker |
| Web Fallback | Tavily Search |
| Evaluation | RAGAS |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Deployment | VPS + Nginx (migrating to Vercel + Render) |

---

## Retrieval Pipeline

Retrieval uses three layers rather than plain vector search:

**1. Ensemble Retrieval (BM25 + Semantic)**

BM25 handles exact keyword matches like regulation numbers ("POJK 77/2016", "Pasal 8 ayat 3"). Semantic search handles meaning-based queries. Both run in parallel with equal weighting and results are merged.

**2. Cross-Encoder Reranking**

The merged results are reranked by a cross-encoder model (Cohere's `rerank-multilingual-v3.0`) which scores each chunk against the query directly. The top 3 chunks are passed to generation.

**3. Agentic Web Fallback**

A grading node uses the LLM to decide whether the retrieved chunks sufficiently answer the question. If not, Tavily web search is triggered as a fallback before generation.

---

## Document Ingestion

Source documents are OJK POJK PDFs from the official OJK website. During ingestion:

- Each document's first page is processed by an LLM to extract a clean, structured title (regulation number, year, topic)
- Documents are split using legal-aware separators that respect Indonesian regulatory structure: `BAB`, `Bagian`, `Pasal`, and `Ayat` boundaries
- Chunks are embedded using Cohere's `embed-multilingual-v3.0`, a multilingual model that handles Bahasa Indonesia accurately

---

## Evaluation (RAGAS)

The pipeline was evaluated using RAGAS on 25 test questions covering OJK fintech, lending, and capital market regulations.

| Metric | Score | Description |
|---|---|---|
| Faithfulness | 1.00 | Answers are fully grounded in retrieved documents |
| Context Recall | 0.96 | Retrieval finds the right chunks 96% of the time |
| Context Precision | 0.75 | Retrieved chunks are relevant to the question |
| Answer Correctness | 0.87 | Overall answer quality against ground truth |

Faithfulness of 1.0 means the system does not hallucinate beyond the retrieved context. The strict grounding prompt explicitly instructs the model to refuse answering when information is not present in the documents.

---

## Project Structure

```
ask-peraturan-ojk/
├── .github/
│   └── workflows/
│       ├── ci.yml          # runs on every push: lint, typecheck, tests
│       └── cd.yml          # runs on merge to main: build, push, deploy
├── backend/
│   ├── main.py             # FastAPI app, streaming endpoint
│   ├── setup_agent.py      # LangGraph agentic workflow
│   ├── ingest.py           # document loading, chunking, indexing
│   ├── utils.py            # retriever and model initialization
│   ├── context.py          # prompt templates
│   ├── config.yaml         # model and retriever configuration
│   └── tests/              # pytest test suite
├── frontend/
│   ├── app/
│   │   ├── page.tsx        # landing page
│   │   └── chat/page.tsx   # chat interface
│   ├── components/
│   │   ├── MessageBubble.tsx
│   │   ├── SourceCard.tsx
│   │   └── QueryInput.tsx
│   └── lib/
│       └── api.ts          # streaming API client
├── docker-compose.yml
├── docker-compose.prod.yml
└── nginx.conf
```

---

## Running Locally

**Prerequisites:** Docker and Docker Compose installed.

**1. Clone the repository**

```bash
git clone https://github.com/FrienDotJava/ask-peraturan-ojk.git
cd ask-peraturan-ojk
```

**2. Set up environment variables**

```bash
cp backend/.env.example backend/.env
```

Add your API keys to `backend/.env`:

```
MISTRAL_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
COHERE_API_KEY=your_key_here
GROQ_API_KEY=your_key_here  # used during ingestion only
```

**3. Add OJK documents**

Place POJK PDF files in `backend/docs/`. You can download them from [ojk.go.id](https://ojk.go.id/id/regulasi/otoritas-jasa-keuangan/peraturan-ojk/default.aspx).

**4. Run ingestion**

```bash
docker compose run --rm backend uv run ingest.py
```

**5. Start the application**

```bash
docker compose up --build
```

The frontend will be available at `http://localhost:3000` and the backend at `http://localhost:8000`.

---

## CI/CD Pipeline

Every push to any branch triggers the CI workflow:

- Python lint with `ruff`
- Python type check with `mypy`
- Backend tests with `pytest`
- TypeScript type check
- Next.js build verification
- Docker image build check

Every merge to `main` triggers the CD workflow:

- Builds and pushes Docker images to GitHub Container Registry
- SSH into the VPS and pulls the new images
- Checks if documents changed and re-runs ingestion if needed
- Rolling restart: backend first, then frontend

---

## Deployment

Currently deployed on a VPS with Nginx as a reverse proxy. Nginx is configured with `proxy_buffering off` to support Server-Sent Events for streaming responses.

Migrated to Vercel (frontend) + Render (backend) for a permanent free-tier deployment.

---

## Limitations

- The knowledge base only covers documents that have been manually ingested. Regulations published after the last ingestion run will not be in the vector store.
- The web search fallback depends on Tavily finding relevant OJK content, which is not always guaranteed.
- Context precision (0.75) indicates some retrieved chunks are not fully relevant. This can be improved with a larger test set and further reranker tuning.

---
