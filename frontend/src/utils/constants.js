export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export const SUPPORTED_FILE_TYPES = [
  '.py', '.md', '.txt', '.rst', '.json', '.yaml', '.yml',
  '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
  '.html', '.htm', '.xml', '.csv', '.js', '.ts', '.java', '.cpp'
];

export const CHAT_MODELS = [
  { value: 'llama3:latest', label: 'Llama 3 (Latest)' },
  { value: 'llama3:8b', label: 'Llama 3 8B' },
  { value: 'llama3:70b', label: 'Llama 3 70B' },
  { value: 'mistral', label: 'Mistral' },
  { value: 'codellama', label: 'Code Llama' }
];

export const EMBEDDING_MODELS = [
  { value: 'BAAI/bge-small-en-v1.5', label: 'BGE Small English' },
  { value: 'BAAI/bge-base-en-v1.5', label: 'BGE Base English' },
  { value: 'sentence-transformers/all-MiniLM-L6-v2', label: 'MiniLM L6' }
];

export const DEFAULT_SETTINGS = {
  chunkSize: 512,
  chunkOverlap: 50,
  retrieveK: 8,
  scoreThreshold: 0.65,
  temperature: 0.1,
  maxTokens: 2048
};

export const COLOR_SCHEMES = {
  light: {
    primary: '#3b82f6',
    secondary: '#6b7280',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    background: '#ffffff',
    surface: '#f8fafc',
    text: '#1f2937'
  },
  dark: {
    primary: '#60a5fa',
    secondary: '#9ca3af',
    success: '#34d399',
    warning: '#fbbf24',
    error: '#f87171',
    background: '#111827',
    surface: '#1f2937',
    text: '#f9fafb'
  }
};