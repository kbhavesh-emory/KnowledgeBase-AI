import logging
from typing import List, Dict, Any
import ollama
import sys
import os

# Add backend to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

logger = logging.getLogger(__name__)

class ChatAgent:
    """LLM Agent with Ollama integration"""
    
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)
        self.model = settings.LLM_MODEL
        logger.info(f"✅ ChatAgent initialized with model: {self.model}")
    
    def generate_response(self, question: str, context: str, 
                         chat_history: List[Dict] = None) -> str:
        """Generate response using RAG context"""
        
        system_prompt = """You are a helpful AI assistant that answers questions based on the provided context.
        
        Guidelines:
        - Use ONLY the provided context to answer the question
        - Be concise and accurate
        - If the context doesn't contain relevant information, say so
        - Format your response using Markdown for readability
        - Include code examples when relevant
        - Cite sources when available"""
        
        user_prompt = f"""Context:
{context}

Question: {question}

Please provide a helpful answer based on the context above:"""
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 2048
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return f"I apologize, but I encountered an error while generating a response. Please try again."
    
    def stream_response(self, question: str, context: str):
        """Stream response token by token"""
        user_prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        
        try:
            stream = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": user_prompt}],
                stream=True
            )
            
            for chunk in stream:
                yield chunk['message']['content']
                
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            yield f"Error: {str(e)}"