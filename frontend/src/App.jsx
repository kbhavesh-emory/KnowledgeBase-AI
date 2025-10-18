import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';
import './styles/App.css';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [activeView, setActiveView] = useState('chat');
  const [savedResponses, setSavedResponses] = useState([]);

  const messagesEndRef = useRef(null);
  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  useEffect(() => scrollToBottom(), [messages]);
  useEffect(() => { document.body.className = darkMode ? 'dark-mode' : ''; }, [darkMode]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;
    const userMessage = { role: 'user', content: inputMessage, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/v1/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputMessage, stream: false })
      });
      if (!res.ok) throw new Error('Network response was not ok');
      const data = await res.json();
      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        messageId: data.message_id
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${err.message}`, isError: true }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const saveResponse = async (question, answer) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/chat/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, answer, tags: ['saved-by-user'] })
      });
      if (res.ok) loadSavedResponses();
    } catch (err) {
      console.error('Save error:', err);
    }
  };

  const loadSavedResponses = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/chat/saved?limit=50`);
      const data = await res.json();
      setSavedResponses(data.responses || []);
    } catch (err) {
      console.error('Load saved error:', err);
    }
  };

  const clearChat = () => {
    if (window.confirm('Clear all messages?')) setMessages([]);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-left">
          <h1>KnowledgeBase AI</h1>
          {/* <span className="app-version">v2.0.0</span> */}
        </div>

        <nav className="header-nav">
          <button className={activeView === 'chat' ? 'nav-btn active' : 'nav-btn'} onClick={() => setActiveView('chat')}>
            Chat
          </button>
          <button
            className={activeView === 'knowledge' ? 'nav-btn active' : 'nav-btn'}
            onClick={() => {
              setActiveView('knowledge');
              loadSavedResponses();
            }}
          >
            Knowledge Base
          </button>
        </nav>

        <div className="header-controls">
          <button className="icon-btn" onClick={clearChat} title="Clear Chat">🗑️</button>
          <button className="icon-btn" onClick={() => setDarkMode(!darkMode)} title="Toggle Theme">
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      {/* Main */}
      <main className="app-main">
        {activeView === 'chat' && (
          <div className="chat-interface">
            <div className="messages-container">
              {messages.length === 0 && (
                <div className="welcome-message">
                  <div className="welcome-icon">🚀</div>
                  <h2>Welcome to KnowledgeBase AI</h2>
                  <p>Ask me anything about your repositories and documents.</p>
                </div>
              )}

              {messages.map((m, i) => (
                <div key={i} className={`message ${m.role}`}>
                  <div className="message-content">
                    <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
                      {m.content}
                    </ReactMarkdown>

                    {m.role === 'assistant' && !m.isError && (
                      <div className="message-actions">
                        <button
                          className="action-btn save-btn"
                          onClick={() => {
                            const userQ = messages[i - 1]?.content || 'Previous question';
                            saveResponse(userQ, m.content);
                          }}
                        >
                          Save
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="message assistant">
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            <div className="input-area">
              <div className="input-container">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about your repositories and documents..."
                  disabled={isLoading}
                  rows="1"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={isLoading || !inputMessage.trim()}
                  className="send-button"
                >
                  {isLoading ? '⏳' : '📤'}
                </button>
              </div>
            </div>
          </div>
        )}

        {activeView === 'knowledge' && (
          <div className="knowledge-panel">
            <div className="panel-header">
              <h2>Saved Knowledge Base</h2>
              <button className="btn-primary" onClick={loadSavedResponses}>Refresh</button>
            </div>

            <div className="saved-responses">
              {savedResponses.length === 0 ? (
                <div className="empty-state">No saved responses yet. Use the Save button in chat.</div>
              ) : (
                savedResponses.map((r) => (
                  <div key={r.id} className="saved-item">
                    <div className="saved-header">
                      <h3 className="saved-question">Q: {r.question}</h3>
                    </div>
                    <div className="saved-answer">
                      <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
                        {r.answer}
                      </ReactMarkdown>
                    </div>
                    <div className="saved-meta">
                      <span>Saved: {new Date(r.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
