#conda --version
#conda info --envs
#conda_on github-chatbot
#conda_off
#conda env list

# crate env  conda install -c conda-forge faiss-gpu python=3.12 -y

Remove 
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
conda remove -n kb-ai --all -y
conda activate knowledgebase-ai
conda deactivate
conda remove -n kb-ai --all -y
curl -I http://127.0.0.1:8000/health

curl -I http://einstein.neurology.emory.edu:8000/health



🧠 Deep-KnowledgeBase-AI

A Local, GPU-Optimized Agentic RAG System for GitHub Repositories & Documents

📘 Overview

Deep-KnowledgeBase-AI is a self-hosted, agentic Retrieval-Augmented Generation (RAG) system.
It allows you to:

🧩 Chat with your documents and GitHub repositories using local LLMs (e.g. llama3:latest via Ollama)

🧠 Index and embed multi-format files (PDFs, Word, Markdown, code, etc.)

💾 Persist knowledge using FAISS vector store & PixelTable database

🧑‍💻 Manage all operations through a powerful Admin Panel

⚡ Run entirely offline (no OpenAI API key required)

🎛️ GPU-optimized for Tesla P100 / CUDA

🏗️ Project Structure
Deep-KnowledgeBase-AI/
│
├── backend/
│   ├── api/
│   │   ├── main.py               # FastAPI entrypoint
│   │   ├── auth.py               # (optional future use)
│   │   ├── admin.py              # Admin panel endpoints (upload, embed, sync)
│   │   ├── chat.py               # Chat API endpoint (LLM inference)
│   │   ├── knowledge.py          # Knowledge base query/save APIs
│   │   └── __init__.py
│   │
│   ├── config/
│   │   ├── settings.py           # Global configuration (models, paths, repos)
│   │   ├── logging.py            # Centralized logging
│   │   └── __init__.py
│   │
│   ├── core/
│   │   ├── agent.py              # LangChain / LLM agent orchestration
│   │   ├── embeddings.py         # SentenceTransformer wrapper (GPU aware)
│   │   ├── rag.py                # RAG pipeline combining retriever + generator
│   │   ├── storage.py            # PixelTable / DuckDB persistence
│   │   └── __init__.py
│   │
│   ├── ingest/
│   │   ├── files.py              # Incremental document ingestion
│   │   └── __init__.py
│   │
│   ├── scripts/
│   │   ├── setup.py              # System setup / initialization
│   │   ├── clone_repos.py        # Clone repositories via GitPython
│   │   ├── embed_documents.py    # Embed all documents in /data/documents
│   │   ├── embed_repositories.py # Embed all source code in /data/repositories
│   │   ├── vectorstore_manage.py # Manage FAISS index (stats, rebuild, query)
│   │   └── sync_repositories.py  # Sync GitHub repos from settings.py
│   │
│   ├── vectorstore/
│   │   ├── faiss_wrapper.py      # FAISS index manager
│   │   ├── manager.py            # Unified vector store manager
│   │   └── __init__.py
│   │
│   ├── data/
│   │   ├── documents/            # Uploaded documents
│   │   ├── repositories/         # Cloned GitHub repositories
│   │   ├── vectorstore/          # FAISS index storage
│   │   └── knowledgebase.db      # PixelTable / DuckDB database
│   │
│   ├── requirements.txt          # Pinned dependencies
│   ├── logging_config.yaml       # (optional logging settings)
│   └── __init__.py
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx               # Main ChatGPT-style UI
│       ├── components/
│       │   ├── AdminPanel.jsx    # Admin panel for uploads, sync, embedding
│       ├── styles/
│       │   ├── App.css           # Unified dark/light responsive design
│       │   └── themes.css
│       ├── constants.js
│       ├── helpers.js
│       ├── useApi.js
│       ├── useStorage.js
│       └── main.jsx
│
├── environment.yml               # Optional conda environment export
├── .env                          # Environment variables (API_PORT, model name, etc.)
└── README.md                     # This file

⚙️ Installation
🐍 1. Create Environment
conda create -n knowledgebase-ai python=3.10 -y
conda activate knowledgebase-ai

📦 2. Install Requirements
pip install -r backend/requirements.txt


If using GPU:

# For CUDA 11.8 or similar:
pip install torch==2.0.1+cu118 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

🧱 3. Frontend Setup
cd frontend
npm install
cd ..

🧩 Configuration
Edit .env or backend/config/settings.py
API_HOST=0.0.0.0
API_PORT=8000
LLM_PROVIDER=ollama
LLM_MODEL=llama3:latest
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
VECTORSTORE_PATH=data/vectorstore
PIXELTABLE_PATH=data/knowledgebase.db

🧠 Running the System
1️⃣ Start Ollama (must have model pulled)
ollama pull llama3:latest
ollama serve &

2️⃣ Initialize Backend
cd backend
python -m scripts.setup -v

3️⃣ Launch FastAPI Server
cd /opt/bhavesh/Deep-KnowledgeBase-AI
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload

4️⃣ Start Frontend
cd frontend
npm run dev


Now open → http://localhost:3000

🧑‍💻 Admin Panel Features

Access via the “Admin” tab in the UI:

Action	Description
📄 Upload Documents	Upload PDFs, Word, Markdown, CSV, etc.
🔄 Sync Repositories	Clone / update GitHub repos (private repos use $GITHUB_TOKEN)
🧠 Embed Documents	Generate embeddings for uploaded files
🧩 Embed Repositories	Generate embeddings for code repositories
🧰 Rebuild Index	Fully reindex all documents + code
📊 View Stats	Check FAISS index size, dimensions, and status
🧱 Data Organization
data/
├── documents/          # Uploaded documents (via admin panel)
├── repositories/       # Cloned GitHub repositories
├── vectorstore/        # FAISS index + metadata
└── knowledgebase.db    # PixelTable persistence

🧮 GPU Optimization
Component	GPU Usage
Embeddings	Uses SentenceTransformers on GPU (bge-small-en-v1.5)
LLM Chat	Uses Ollama model (Llama3) with CUDA backend
Indexing	FAISS compiled with BLAS acceleration

To verify GPU:

python - <<'PY'
import torch
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Device:", torch.cuda.get_device_name(0))
PY

🧰 Admin CLI (optional)

You can run these directly from the backend:

# Clone or update all repos
python -m backend.scripts.sync_repositories

# Embed all documents
python -m backend.scripts.embed_documents --path data/documents

# Embed all repositories
python -m backend.scripts.embed_repositories --path data/repositories

# Check FAISS index stats
python -m backend.scripts.vectorstore_manage stats

🧩 Frontend Features

ChatGPT-style layout (markdown, syntax highlighting)

Dark / light mode

Save responses to KnowledgeBase

View KnowledgeBase entries

Admin panel for upload / sync / embedding

Responsive design for desktop and mobile

📊 Example Workflow

Go to Admin Panel → Upload ResearchPaper.pdf

Click Embed Documents

Paste GitHub repo URLs → Sync Repositories

Click Embed Repositories

Switch to Chat tab → Ask:

“Summarize the pipeline steps in bdsa-workflows-slurm.”

🧩 Export Current Environment (Freeze)

Once working perfectly:

pip freeze > backend/requirements.txt
conda env export --no-builds > environment.yml

🧩 Recreate Anywhere
conda env create -f environment.yml
conda activate knowledgebase-ai
pip install -r backend/requirements.txt

🔐 Private Repositories

Before running sync commands:

export GITHUB_TOKEN=ghp_your_token_here

🛡️ Troubleshooting
Issue	Solution
ImportError: attempted relative import beyond top-level package	Always run commands from project root (/Deep-KnowledgeBase-AI)
Ollama refused connection	Run ollama serve & before starting backend
Failed to connect to port 8000	Ensure Uvicorn running on correct port (sudo ufw allow 8000/tcp)
torch.cuda not compatible	Install torch version matching your CUDA (e.g. 2.0.1+cu118 for Tesla P100)
🧾 License

© 2025 Bhavesh —
Developed at Emory University – School of Medicine.
All rights reserved for internal research and educational use.

🧩 Credits

LangChain, SentenceTransformers, FAISS

Ollama for local LLM inference

PixelTable for knowledge persistence

FastAPI + React (Vite) for modern web interface
