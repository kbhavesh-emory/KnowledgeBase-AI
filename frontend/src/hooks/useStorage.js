import { useState, useCallback } from 'react';
import { useApi } from './useApi';

export const useStorage = () => {
  const [savedResponses, setSavedResponses] = useState([]);
  const [knowledgeStats, setKnowledgeStats] = useState(null);
  const { apiCall, loading, error } = useApi();

  const saveResponse = useCallback(async (question, answer, sources = []) => {
    try {
      const data = await apiCall('/api/v1/chat/save', {
        method: 'POST',
        body: JSON.stringify({
          question,
          answer,
          sources,
          tags: ['saved-by-user'],
        }),
      });

      if (data.success) {
        // Refresh the list
        loadSavedResponses();
        loadKnowledgeStats();
      }

      return data;
    } catch (err) {
      console.error('Save error:', err);
      throw err;
    }
  }, [apiCall]);

  const loadSavedResponses = useCallback(async (limit = 100) => {
    try {
      const data = await apiCall(`/api/v1/chat/saved?limit=${limit}`);
      setSavedResponses(data.responses || []);
      return data;
    } catch (err) {
      console.error('Load saved error:', err);
      throw err;
    }
  }, [apiCall]);

  const deleteResponse = useCallback(async (responseId) => {
    try {
      const data = await apiCall(`/api/v1/knowledge/response/${responseId}`, {
        method: 'DELETE',
      });

      if (data.success) {
        // Refresh the list
        loadSavedResponses();
        loadKnowledgeStats();
      }

      return data;
    } catch (err) {
      console.error('Delete error:', err);
      throw err;
    }
  }, [apiCall, loadSavedResponses]);

  const loadKnowledgeStats = useCallback(async () => {
    try {
      const data = await apiCall('/api/v1/knowledge/stats');
      setKnowledgeStats(data);
      return data;
    } catch (err) {
      console.error('Load stats error:', err);
      throw err;
    }
  }, [apiCall]);

  const exportKnowledgeBase = useCallback(async () => {
    try {
      const data = await apiCall('/api/v1/knowledge/export');
      
      // Create and download JSON file
      const blob = new Blob([JSON.stringify(data.data, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `knowledge-base-export-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      return data;
    } catch (err) {
      console.error('Export error:', err);
      throw err;
    }
  }, [apiCall]);

  return {
    savedResponses,
    knowledgeStats,
    saveResponse,
    loadSavedResponses,
    deleteResponse,
    loadKnowledgeStats,
    exportKnowledgeBase,
    loading,
    error,
  };
};