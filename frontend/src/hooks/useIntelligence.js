import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

/**
 * Hook to manage intelligence signals and rankings.
 * Connects to the FastAPI backend.
 */
export const useIntelligence = () => {
  const [rankings, setRankings] = useState([]);
  const [alpha, setAlpha] = useState(null);
  const [briefing, setBriefing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Conflux Weights (default match constants)
  const [weights, setWeights] = useState({
    w_sports: 0.40,
    w_markets: 0.25,
    w_finance: 0.15,
    w_climate: 0.10,
    w_social: 0.10
  });

  const fetchRankings = useCallback(async () => {
    try {
      const params = new URLSearchParams(
        Object.entries(weights).reduce((acc, [k, v]) => ({ ...acc, [k]: v.toString() }), {})
      );
      const response = await axios.get(`/v1/predict/wc2026/rankings?${params}`);
      setRankings(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch intelligence rankings');
      console.error(err);
    }
  }, [weights]);

  const fetchAlpha = async () => {
    try {
      const response = await axios.get('/v1/alpha/opportunities');
      setAlpha(response.data);
    } catch (err) {
      console.error('Alpha fetch failed', err);
    }
  };

  const fetchBriefing = async () => {
    try {
      const response = await axios.get('/v1/analyst/briefing');
      setBriefing(response.data);
    } catch (err) {
      console.error('Briefing fetch failed', err);
    }
  };

  useEffect(() => {
    setLoading(true);
    const init = async () => {
      await Promise.all([fetchRankings(), fetchAlpha(), fetchBriefing()]);
      setLoading(false);
    };
    init();
    
    // Poll for alpha updates every 30s
    const interval = setInterval(fetchAlpha, 30000);
    return () => clearInterval(interval);
  }, [fetchRankings]);

  const updateWeight = (key, val) => {
    setWeights(prev => ({ ...prev, [key]: val }));
  };

  return {
    rankings,
    alpha,
    briefing,
    weights,
    updateWeight,
    loading,
    error,
    refresh: fetchRankings
  };
};
