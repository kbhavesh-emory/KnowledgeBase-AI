import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';

const Message = ({ message, onSave }) => {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';
  const isError = message.isError;

  return (
    <div className={`message ${message.role} ${isError ? 'error' : ''}`}>
      <div className="message-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="message-content">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]} 
          rehypePlugins={[rehypeHighlight]}
        >
          {message.content}
        </ReactMarkdown>
        
        {message.sources && message.sources.length > 0 && (
          <div className="sources">
            <div className="sources-title">📚 Sources</div>
            <div className="sources-list">
              {message.sources.map((source, idx) => (
                <span 
                  key={idx} 
                  className="source-tag" 
                  title={source.content_preview}
                >
                  {source.source} ({(source.score * 100).toFixed(1)}%)
                </span>
              ))}
            </div>
          </div>
        )}
        
        {isAssistant && !isError && (
          <div className="message-actions">
            <button 
              className="action-btn save-btn"
              onClick={onSave}
              title="Save to Knowledge Base"
            >
              ⭐ Save
            </button>
            <span className="message-time">
              {new Date(message.timestamp).toLocaleTimeString()}
            </span>
          </div>
        )}
        
        {isError && (
          <div className="error-banner">
            ⚠️ There was an error generating this response
          </div>
        )}
      </div>
    </div>
  );
};

export default Message;