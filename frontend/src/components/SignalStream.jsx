import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, Activity, Shield, Zap } from 'lucide-react';

const SignalStream = () => {
  const [logs, setLogs] = useState([
    { id: 1, type: 'info', text: 'Neural Uplink Stable. Monitoring 48 entities.', time: '0.0s' },
    { id: 2, type: 'alert', text: 'Social signal spike detected for Team Portugal.', time: '1.2s' },
    { id: 3, type: 'climate', text: 'Atmospheric pressure rising at Estadio Azteca.', time: '2.5s' }
  ]);

  const activities = [
    "Recalculating financial delta for Argentina...",
    "Alpha discovered: Underpriced market in Group G.",
    "Scanning social sentiment for 12.4M nodes.",
    "Stress test: Heatwave simulation in Miami Gardens.",
    "Market calibration complete for Brazil vs Spain.",
    "Zerve Analyst: New insight generated for Group D.",
    "Updating sports form signal: England +0.12pp."
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      const newLog = {
        id: Date.now(),
        type: ['info', 'alert', 'climate', 'zap'][Math.floor(Math.random() * 4)],
        text: activities[Math.floor(Math.random() * activities.length)],
        time: (Math.random() * 5).toFixed(1) + 's'
      };
      setLogs(prev => [newLog, ...prev.slice(0, 5)]);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="terminal-card bg-bg1/20 border-white/5 h-[300px] flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-[10px] font-mono font-bold text-white/40 tracking-[0.2em] uppercase flex items-center gap-2">
          <Terminal size={12} className="text-amber" /> Neural Signal Stream
        </h3>
        <div className="flex gap-1">
          <div className="w-1 h-1 rounded-full bg-teal animate-pulse" />
          <div className="w-1 h-1 rounded-full bg-amber animate-pulse" />
        </div>
      </div>
      
      <div className="flex-1 space-y-3 font-mono overflow-hidden">
        <AnimatePresence>
          {logs.map((log) => (
            <motion.div
              key={log.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="flex gap-3 text-[10px] leading-relaxed border-b border-white/[0.02] pb-2 last:border-0"
            >
              <span className="text-white/10 shrink-0">[{log.time}]</span>
              <span className={`shrink-0 uppercase font-bold ${
                log.type === 'alert' ? 'text-amber' : 
                log.type === 'climate' ? 'text-red' : 
                log.type === 'zap' ? 'text-teal' : 'text-white/30'
              }`}>
                {log.type}
              </span>
              <span className="text-white/50 truncate">{log.text}</span>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      <div className="mt-4 pt-4 border-t border-white/5 flex justify-between items-center">
        <div className="flex items-center gap-2">
           <Activity size={10} className="text-teal" />
           <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest">IO: 1.2 GB/S</span>
        </div>
        <span className="text-[8px] font-mono text-white/20 uppercase">Encryption: AES-256</span>
      </div>
    </div>
  );
};

export default SignalStream;
