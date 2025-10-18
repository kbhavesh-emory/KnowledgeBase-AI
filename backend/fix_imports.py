#!/usr/bin/env python3
"""
Script to fix import issues in the KnowledgeBase AI project
"""

import os
import fileinput
import sys

# Files to fix with their import replacements
files_to_fix = {
    "backend/api/main.py": {
        "from .routes import chat, knowledge, admin": "from api.routes import chat, knowledge, admin",
        "from ..core.rag import RAGSystem": "from core.rag import RAGSystem",
        "from ..core.storage import KnowledgeStorage": "from core.storage import KnowledgeStorage",
        "from ..config.settings import settings": "from config.settings import settings",
        "from ..config.logging import setup_logging": "from config.logging import setup_logging"
    },
    "backend/api/routes/chat.py": {
        "from ...core.rag import RAGSystem": "from core.rag import RAGSystem",
        "from ...core.agent import ChatAgent": "from core.agent import ChatAgent", 
        "from ...core.storage import KnowledgeStorage": "from core.storage import KnowledgeStorage"
    },
    "backend/api/routes/knowledge.py": {
        "from ...core.storage import KnowledgeStorage": "from core.storage import KnowledgeStorage",
        "from ...ingest.processor import FileProcessor": "from ingest.processor import FileProcessor",
        "from ...core.rag import RAGSystem": "from core.rag import RAGSystem"
    },
    "backend/api/routes/admin.py": {
        "from ...core.rag import RAGSystem": "from core.rag import RAGSystem",
        "from ...ingest.github import GitHubLoader": "from ingest.github import GitHubLoader",
        "from ...config.settings import settings": "from config.settings import settings"
    }
}

def fix_imports():
    print("🔧 Fixing import issues...")
    
    for filepath, replacements in files_to_fix.items():
        if os.path.exists(filepath):
            print(f"Fixing {filepath}...")
            with fileinput.FileInput(filepath, inplace=True) as file:
                for line in file:
                    for old, new in replacements.items():
                        if old in line:
                            line = line.replace(old, new)
                            print(f"  Replaced: {old.strip()} -> {new.strip()}")
                    print(line, end='')
        else:
            print(f"⚠️  File not found: {filepath}")
    
    print("✅ Import fixes completed!")

if __name__ == "__main__":
    fix_imports()
