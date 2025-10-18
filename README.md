# KnowledgeBase-AI  
> **A Local, GPU-Optimized Agentic RAG System for GitHub Repositories & Documents**

---

## Overview

**KnowledgeBase-AI** is a fully local, end-to-end **Retrieval-Augmented Generation (RAG)** and **Knowledge Management** system.  
It enables you to chat with your **research documents**, **GitHub repositories**, and **scientific codebases** — all powered by local **LLMs via Ollama**.

### ✨ Features
- 🧠 **RAG pipeline** over documents & repositories  
- 🧩 **GPU-accelerated embeddings** using SentenceTransformers  
- ⚡ **Local LLM inference** via Ollama (`llama3:latest`)  
- 💾 **FAISS vectorstore + PixelTable persistence**  
- 🔐 **Offline-first**, no external API keys required  

---

## Project Structure

```bash
KnowledgeBase-AI/
│
├── backend/
│   ├── api/
│   │   ├── main.py               # FastAPI entrypoint
│   │   ├── admin.py              # Admin endpoints (upload, sync, embed)
│   │   ├── chat.py               # Chat API
│   │   ├── knowledge.py          # Saved knowledge APIs
│   │   └── auth.py               # (Optional future use)
│   │
│   ├── config/
│   │   ├── settings.py           # System configuration
│   │   ├── logging.py            # Logging utilities
│   │   └── __init__.py
│   │
│   ├── core/
│   │   ├── agent.py              # Ollama LangChain agent
│   │   ├── embeddings.py         # GPU embedding manager
│   │   ├── rag.py                # Retrieval + Generation pipeline
│   │   ├── storage.py            # PixelTable knowledge storage
│   │   └── __init__.py
│   │
│   ├── ingest/
│   │   └── files.py              # Incremental document processing
│   │
│   ├── scripts/
│   │   ├── setup.py              # Initialize environment
│   │   ├── embed_documents.py    # Embed documents
│   │   ├── embed_repositories.py # Embed code repositories
│   │   ├── vectorstore_manage.py # FAISS maintenance
│   │   └── sync_repositories.py  # Clone + sync GitHub repos
│   │
│   ├── vectorstore/
│   │   ├── faiss_wrapper.py      # FAISS index handling
│   │   ├── manager.py            # Vector store manager
│   │   └── __init__.py
│   │
│   ├── data/
│   │   ├── documents/            # Uploaded documents
│   │   ├── repositories/         # Cloned GitHub repos
│   │   ├── vectorstore/          # FAISS index
│   │   └── knowledgebase.db      # PixelTable DB
│   │
│   └── requirements.txt          # Frozen dependencies
│
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx               # Main chat app
│   │   ├── components/AdminPanel.jsx
│   │   ├── styles/App.css
│   │   ├── themes.css
│   │   └── main.jsx
│
├── environment.yml               # Conda environment export
├── .env                          # Environment variables
└── README.md                     # This file
```

---

## Installation

### Create environment
```bash
conda create -n knowledgebase-ai python=3.10 -y
conda activate knowledgebase-ai
```

### Install dependencies
```bash
pip install -r backend/requirements.txt
```

If you have a GPU (Tesla P100):
```bash
pip install torch==2.0.1+cu118 torchvision torchaudio   --index-url https://download.pytorch.org/whl/cu118
```

### Frontend setup
```bash
cd frontend
npm install
cd ..
```

---

## Configuration

Edit `.env` or `backend/config/settings.py`:

```bash
API_HOST=0.0.0.0
API_PORT=8000
LLM_PROVIDER=ollama
LLM_MODEL=llama3:latest
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
VECTORSTORE_PATH=data/vectorstore
PIXELTABLE_PATH=data/knowledgebase.db
```

---

## Run the System

### 1️⃣ Start Ollama
```bash
ollama pull llama3:latest
ollama serve &
```

### 2️⃣ Initialize the system
```bash
cd backend
python -m scripts.setup -v
```

### 3️⃣ Launch backend
```bash
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4️⃣ Launch frontend
```bash
cd frontend
npm run dev
```
Open [http://localhost:3000](http://localhost:3000)


