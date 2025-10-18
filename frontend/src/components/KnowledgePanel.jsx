import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';

const KnowledgePanel = () => {
  const [savedResponses, setSavedResponses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  const loadSavedResponses = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/chat/saved?limit=100');
      const data = await response.json();
      setSavedResponses(data.responses || []);
    } catch (error) {
      console.error('Load saved error:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/v1/knowledge/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Load stats error:', error);
    }
  };

  const deleteResponse = async (responseId) => {
    if (window.confirm('Are you sure you want to delete this response?')) {
      try {
        const response = await fetch(`/api/v1/knowledge/response/${responseId}`, {
          method: 'DELETE'
        });
        
        if (response.ok) {
          loadSavedResponses();
          loadStats();
        }
      } catch (error) {
        console.error('Delete error:', error);
        alert('Failed to delete response');
      }
    }
  };

  useEffect(() => {
    loadSavedResponses();
    loadStats();
  }, []);

  if (loading) {
    return (
      <div className="knowledge-panel">
        <div className="loading-state">Loading knowledge base...</div>
      </div>
    );
  }

  return (
    <div className="knowledge-panel">
      <div className="panel-header">
        <h2>📚 Knowledge Base</h2>
        <div className="header-actions">
          {stats && (
            <div className="stats-badge">
              {stats.total_responses} saved responses
            </div>
          )}
          <button className="btn-primary" onClick={loadSavedResponses}>
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="saved-responses">
        {savedResponses.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📝</div>
            <h3>No saved responses yet</h3>
            <p>Use the ⭐ button in chat to save helpful responses to your knowledge base.</p>
          </div>
        ) : (
          savedResponses.map((response) => (
            <div key={response.id} className="saved-item">
              <div className="saved-header">
                <h3 className="saved-question">Q: {response.question}</h3>
                <button 
                  className="btn-danger"
                  onClick={() => deleteResponse(response.id)}
                  title="Delete response"
                >
                  🗑️ Delete
                </button>
              </div>
              
              <div className="saved-answer">
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]} 
                  rehypePlugins={[rehypeHighlight]}
                >
                  {response.answer}
                </ReactMarkdown>
              </div>
              
              <div className="saved-meta">
                <span className="meta-item">
                  📅 {new Date(response.created_at).toLocaleDateString()}
                </span>
                {response.model_used && (
                  <span className="meta-item">
                    🤖 {response.model_used}
                  </span>
                )}
                {response.tags && JSON.parse(response.tags).length > 0 && (
                  <span className="meta-item">
                    🏷️ {JSON.parse(response.tags).join(', ')}
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default KnowledgePanel;