"use client";

import { useState, useEffect } from 'react';

interface HealthResponse {
  status: string;
  uptime_seconds?: number;
}

export const BackendStatus = () => {
  const [status, setStatus] = useState<'online' | 'offline' | 'loading'>('loading');
  const [uptime, setUptime] = useState<number | null>(null);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;
    const POLL_INTERVAL = 10000; // 10 seconds

    const checkHealth = async () => {
      try {
        const res = await fetch('http://localhost:8000/rpc/health');
        if (res.ok) {
          const data: HealthResponse = await res.json();
          setStatus('online');
          setUptime(data.uptime_seconds ?? null);
        } else {
          setStatus('offline');
        }
      } catch (err) {
        setStatus('offline');
      }
    };

    const handleVisibilityChange = () => {
      if (document.hidden) {
        clearInterval(intervalId);
      } else {
        checkHealth();
        intervalId = setInterval(checkHealth, POLL_INTERVAL);
      }
    };

    // Initial check
    checkHealth();
    intervalId = setInterval(checkHealth, POLL_INTERVAL);

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      clearInterval(intervalId);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      padding: '4px 12px',
      borderRadius: '20px',
      backgroundColor: 'rgba(255, 255, 255, 0.05)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      fontSize: '0.85rem',
      color: '#fff'
    }}>
      <div style={{
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        backgroundColor: status === 'online' ? '#4ade80' : (status === 'offline' ? '#f87171' : '#fbbf24'),
        boxShadow: `0 0 8px ${status === 'online' ? '#4ade80' : (status === 'offline' ? '#f87171' : '#fbbf24')}`
      }} />
      <span>
        Backend: {status.charAt(0).toUpperCase() + status.slice(1)}
        {status === 'online' && uptime !== null && ` (${uptime}s)`}
      </span>
    </div>
  );
};
