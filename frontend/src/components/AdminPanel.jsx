import React, { useState, useEffect } from 'react';

const AdminPanel = () => {
  const [systemStatus, setSystemStatus] = useState(null);
  const [indexStats, setIndexStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [repoUrls, setRepoUrls] = useState('');

  const loadSystemStatus = async () => {
    try {
      const response = await fetch('/api/v1/admin/status');
      const data = await response.json();
      setSystemStatus(data);
    } catch (error) {
      console.error('Load status error:', error);
    }
  };

  const loadIndexStats = async () => {
    try {
      const response = await fetch('/api/v1/admin/index/stats');
      const data = await response.json();
      setIndexStats(data);
    } catch (error) {
      console.error('Load index stats error:', error);
    }
  };

  const loadRepositories = async () => {
    if (!repoUrls.trim()) return;

    const urls = repoUrls.split('\n').filter(url => url.trim());
    
    try {
      const response = await fetch('/api/v1/admin/repositories/load', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_urls: urls })
      });
      
      const data = await response.json();
      alert(data.message);
      setRepoUrls('');
      
    } catch (error) {
      console.error('Load repos error:', error);
      alert('Failed to load repositories');
    }
  };

  const rebuildIndex = async () => {
    if (window.confirm('Are you sure you want to rebuild the index? This may take a while.')) {
      try {
        const response = await fetch('/api/v1/admin/index/rebuild', {
          method: 'POST'
        });
        
        const data = await response.json();
        alert(data.message);
        
      } catch (error) {
        console.error('Rebuild error:', error);
        alert('Failed to rebuild index');
      }
    }
  };

  useEffect(() => {
    loadSystemStatus();
    loadIndexStats();
    setLoading(false);
    
    // Refresh status every 30 seconds
    const interval = setInterval(loadSystemStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="admin-panel">Loading admin panel...</div>;
  }

  return (
    <div className="admin-panel">
      <h2>⚙️ System Administration</h2>

      {/* System Status */}
      <div className="admin-section">
        <h3>System Status</h3>
        {systemStatus ? (
          <div className="status-grid">
            <div className="status-card">
              <h4>CPU Usage</h4>
              <div className="status-value">{systemStatus.cpu_percent}%</div>
            </div>
            <div className="status-card">
              <h4>Memory Usage</h4>
              <div className="status-value">{systemStatus.memory_percent}%</div>
            </div>
            <div className="status-card">
              <h4>Disk Usage</h4>
              <div className="status-value">{systemStatus.disk_usage.percent}%</div>
            </div>
            {systemStatus.gpu_info.length > 0 && (
              <div className="status-card">
                <h4>GPU Usage</h4>
                <div className="status-value">
                  {systemStatus.gpu_info[0].load.toFixed(1)}%
                </div>
              </div>
            )}
          </div>
        ) : (
          <div>Unable to load system status</div>
        )}
      </div>

      {/* Index Stats */}
      <div className="admin-section">
        <h3>Vector Index</h3>
        {indexStats ? (
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Documents:</span>
              <span className="stat-value">{indexStats.document_count}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Dimensions:</span>
              <span className="stat-value">{indexStats.embedding_dim}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Index Type:</span>
              <span className="stat-value">{indexStats.index_type}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Score Threshold:</span>
              <span className="stat-value">{indexStats.score_threshold}</span>
            </div>
          </div>
        ) : (
          <div>Unable to load index stats</div>
        )}
        
        <button className="btn-warning" onClick={rebuildIndex}>
          🔄 Rebuild Index
        </button>
      </div>

      {/* Repository Management */}
      <div className="admin-section">
        <h3>Repository Management</h3>
        <div className="form-group">
          <label>GitHub Repository URLs (one per line):</label>
          <textarea
            value={repoUrls}
            onChange={(e) => setRepoUrls(e.target.value)}
            placeholder="https://github.com/username/repo1&#10;https://github.com/username/repo2"
            rows="4"
          />
        </div>
        <button 
          className="btn-primary" 
          onClick={loadRepositories}
          disabled={!repoUrls.trim()}
        >
          📥 Load Repositories
        </button>
      </div>

      {/* System Actions */}
      <div className="admin-section">
        <h3>System Actions</h3>
        <div className="action-buttons">
          <button className="btn-secondary" onClick={loadSystemStatus}>
            🔄 Refresh Status
          </button>
          <button className="btn-info" onClick={loadIndexStats}>
            📊 Refresh Index Stats
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;