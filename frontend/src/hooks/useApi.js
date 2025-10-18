import { useState, useCallback } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const apiCall = useCallback(async (endpoint, options = {}) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;

    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return {
    loading,
    error,
    apiCall,
    clearError,
  };
};

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(false);
  const { apiCall, loading, error } = useApi();

  const sendMessage = async (message, stream = false) => {
    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);

    if (stream) {
      await streamMessage(message);
    } else {
      await regularMessage(message);
    }
  };

  const regularMessage = async (message) => {
    try {
      const data = await apiCall('/api/v1/chat', {
        method: 'POST',
        body: JSON.stringify({
          message,
          stream: false,
        }),
      });

      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        sources: data.sources,
        messageId: data.message_id,
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      const errorMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${err.message}`,
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const streamMessage = async (message) => {
    setStreaming(true);
    
    try {
      const response = await fetch(`${API_BASE}/api/v1/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          stream: true,
        }),
      });

      if (!response.ok) throw new Error('Stream request failed');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedContent = '';

      const assistantMessage = {
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
        sources: [],
        isStreaming: true,
      };

      setMessages(prev => [...prev, assistantMessage]);

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            
            if (data === '[DONE]') {
              setStreaming(false);
              setMessages(prev => prev.map(msg => 
                msg.isStreaming ? { ...msg, isStreaming: false } : msg
              ));
              return;
            }

            try {
              const parsed = JSON.parse(data);
              
              if (parsed.content) {
                accumulatedContent += parsed.content;
                
                setMessages(prev => prev.map(msg => 
                  msg.isStreaming 
                    ? { ...msg, content: accumulatedContent }
                    : msg
                ));
              }
            } catch (e) {
              console.warn('Failed to parse stream chunk:', e);
            }
          }
        }
      }
    } catch (err) {
      setStreaming(false);
      const errorMessage = {
        role: 'assistant',
        content: `Streaming error: ${err.message}`,
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const clearMessages = () => setMessages([]);

  return {
    messages,
    sendMessage,
    clearMessages,
    loading: loading || streaming,
    error,
    streaming,
  };
};