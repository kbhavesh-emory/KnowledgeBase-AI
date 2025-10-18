#!/bin/bash

echo "🚀 Starting KnowledgeBase AI on einstein.neurology.emory.edu"

# Activate environment
conda activate knowledgebase-ai

# Check Ollama
echo "🔍 Starting Ollama..."
ollama serve > /dev/null 2>&1 &
sleep 5

# Start backend
echo "🌐 Starting backend API..."
cd /opt/bhavesh/Deep-KnowledgeBase-AI
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
npm run dev -- --host 0.0.0.0 > frontend.log 2>&1 &

echo "✅ Services started!"
echo "   Frontend: http://einstein.neurology.emory.edu:3000"
echo "   Backend:  http://einstein.neurology.emory.edu:8000"
echo "   API Docs: http://einstein.neurology.emory.edu:8000/docs"
echo ""
echo "📋 Check logs:"
echo "   Backend:  tail -f /opt/bhavesh/Deep-KnowledgeBase-AI/backend.log"
echo "   Frontend: tail -f /opt/bhavesh/Deep-KnowledgeBase-AI/frontend/frontend.log"
