GPU Optimization
The system is optimized for P100 GPU with:

Mixed precision (FP16) training

Batch processing (8,000 chunks/batch)

Memory management and automatic cleanup

Conservative batch sizes to prevent OOM

📊 Usage
Adding Data
Upload Documents: Use the admin panel to upload documents

Clone Repositories: Add GitHub repository URLs in the admin panel

Process Directories: Use the scripts to process local directories

Chat Interface
Ask questions about your documents and repositories

View sources for each answer

Save important responses with the ⭐ button

Real-time streaming responses

Knowledge Base
View all saved responses

Search and filter saved knowledge

Export knowledge base as JSON

🚀 Performance
Embedding Speed: ~1000 documents/minute on P100

Query Response: < 2 seconds for most queries

Memory Usage: Optimized for 16GB GPU memory

Storage: Compressed embeddings with FAISS optimization

🔍 API Endpoints
POST /api/v1/chat - Send chat message

POST /api/v1/chat/save - Save response to knowledge base

GET /api/v1/chat/saved - Get saved responses

POST /api/v1/knowledge/upload - Upload document

GET /api/v1/admin/status - System status

POST /api/v1/admin/repositories/load - Load GitHub repositories

# Project Structure

KnowledgeBase-AI/
├── backend/                 # FastAPI backend
│   ├── api/               # API routes and middleware
│   ├── core/              # Core system components
│   ├── ingest/            # Document processing
│   ├── vectorstore/       # FAISS vector store
│   └── scripts/           # Management scripts
├── frontend/              # React/Vite frontend
│   └── src/
│       ├── components/    # React components
│       ├── hooks/         # Custom React hooks
│       └── styles/        # CSS stylesheets
├── data/                  # Data storage
│   ├── repositories/      # Cloned GitHub repos
│   ├── documents/         # Uploaded documents
│   └── vectorstore/       # FAISS indices
└── docker/               # Docker configuration

# Access the application:

Frontend: http://localhost:3000

Backend API: http://localhost:8000

API Documentation: http://localhost:8000/docs

# Docker Setup
docker-compose -f docker/docker-compose.yml up -d

KnowledgeBase-AI/
├── backend/                 # FastAPI backend
│   ├── api/               # API routes and middleware
│   ├── core/              # Core system components
│   ├── ingest/            # Document processing
│   ├── vectorstore/       # FAISS vector store
│   └── scripts/           # Management scripts
├── frontend/              # React/Vite frontend
│   └── src/
│       ├── components/    # React components
│       ├── hooks/         # Custom React hooks
│       └── styles/        # CSS stylesheets
├── data/                  # Data storage
│   ├── repositories/      # Cloned GitHub repos
│   ├── documents/         # Uploaded documents
│   └── vectorstore/       # FAISS indices
└── docker/               # Docker configuration



# Steps 

cd backend
source .venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000


CPU
pip install torch --index-url https://download.pytorch.org/whl/cpu
GPU
pip install torch --index-url https://download.pytorch.org/whl/cu121


Step 1: Start Required Services
Terminal 1 - Start Ollama (LLM Service)

bash
# Make sure Ollama is running with your model
ollama serve &
ollama pull llama3:latest

# Verify Ollama is working
curl http://localhost:11434/api/tags
Step 2: Start the Backend
Terminal 2 - Backend Server

bash
# Navigate to your project
cd /opt/bhavesh/Deep-KnowledgeBase-AI

# Activate your conda environment
conda activate knowledgebase-ai

# Start the FastAPI backend
cd backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
Step 3: Start the Frontend
Terminal 3 - Frontend Development Server

bash
# Navigate to frontend (new terminal)
cd /opt/bhavesh/Deep-KnowledgeBase-AI/frontend

# Install frontend dependencies (if not done)
npm install

# Start the development server
npm run dev
✅ Verification Steps
Check Backend API
bash
# Test if backend is running
curl http://localhost:8000/health

# Check API documentation
# Open in browser: http://localhost:8000/docs
Check Frontend
Open browser: http://localhost:3000

You should see the ChatGPT-style interface

📁 Project Structure Overview
text
Deep-KnowledgeBase-AI/
├── backend/
│   ├── api/main.py              # FastAPI server
│   ├── core/                    # RAG, embeddings, storage
│   ├── ingest/                  # Document processing
│   └── vectorstore/             # FAISS vector store
├── frontend/
│   ├── src/App.jsx              # Main React app
│   └── package.json             # Frontend dependencies
├── data/
│   ├── documents/               # Your documents go here
│   ├── vectorstore/             # FAISS indices
│   └── knowledgebase.db         # SQLite knowledge base
└── requirements.txt             # Python dependencies
🎯 Adding Your First Documents
Option A: Add Documents via UI
Go to http://localhost:3000

Use the upload feature in the admin panel

Upload PDFs, Word docs, text files, etc.

Option B: Add Documents via API
bash
# Create a test document
echo "This is a test document about artificial intelligence and machine learning." > test_doc.txt

# Upload via API (if you have the endpoint)
curl -X POST "http://localhost:8000/api/v1/knowledge/upload" \
  -F "file=@test_doc.txt"
Option C: Add GitHub Repositories
bash
# Via admin panel at http://localhost:3000
# Or via API
curl -X POST "http://localhost:8000/api/v1/admin/repositories/load" \
  -H "Content-Type: application/json" \
  -d '{"repo_urls": ["https://github.com/username/repo"]}'
💬 Testing the Chat Interface
Open http://localhost:3000

Ask questions like:

"What documents do you have?"

"Explain artificial intelligence"

"What is machine learning?"

Save responses using the ⭐ button

View saved responses in the Knowledge Base tab

🔧 Troubleshooting Common Issues
If Backend Fails to Start:
bash
# Check if all dependencies are installed
python -c "import fastapi, langchain, sentence_transformers, torch, faiss; print('All imports OK')"

# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check port availability
netstat -tulpn | grep 8000
If Frontend Fails to Start:
bash
# Reinstall frontend dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
If GPU Acceleration Isn't Working:
bash
# Verify GPU detection
python -c "
import torch
print(f'CUDA: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
"
📊 Monitoring Your System
Check System Status:
bash
# Backend health
curl http://localhost:8000/health

# System status
curl http://localhost:8000/api/v1/admin/status

# Vector store stats
curl http://localhost:8000/api/v1/admin/index/stats
Check Logs:
bash
# Backend logs (in the terminal running uvicorn)
# Application logs
tail -f logs/application.log
🚀 Production Deployment Tips
When ready for production:

Use production server:

bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
Build frontend for production:

bash
cd frontend
npm run build
Use process manager (PM2, systemd):

bash
pm2 start "uvicorn api.main:app --host 0.0.0.0 --port 8000" --name knowledgebase-ai
🎉 You're Ready!
Your KnowledgeBase AI should now be fully operational with:

✅ GPU-accelerated embeddings (P100)

✅ ChatGPT-style interface

✅ Document processing (PDF, Word, Excel, code files)

✅ GitHub repository integration

✅ Knowledge base saving (⭐ button)

✅ Real-time RAG responses

Start with Step 1 (Ollama), then Step 2 (Backend), then Step 3 (Frontend). The system will be available at http://localhost:3000! 🚀

Deep-KnowledgeBase-AI/
├── backend/
│   ├── api/main.py              # FastAPI server
│   ├── core/                    # RAG, embeddings, storage
│   ├── ingest/                  # Document processing
│   └── vectorstore/             # FAISS vector store
├── frontend/
│   ├── src/App.jsx              # Main React app
│   └── package.json             # Frontend dependencies
├── data/
│   ├── documents/               # Your documents go here
│   ├── vectorstore/             # FAISS indices
│   └── knowledgebase.db         # SQLite knowledge base
└── requirements.txt             # Python dependencies# KnowledgeBase-AI
