import React from 'react';
import { motion } from 'framer-motion';

const IntelligenceControls = ({ weights, onWeightChange }) => {
  const controls = [
    { key: 'w_sports',  label: 'Sports Form', icon: '⚽', color: 'text-blue' },
    { key: 'w_markets', label: 'Market Bias', icon: '📈', color: 'text-amber' },
    { key: 'w_finance', label: 'Econ Stability', icon: '💰', color: 'text-teal' },
    { key: 'w_climate', label: 'Climate Risk', icon: '🌩', color: 'text-red' },
    { key: 'w_social',  label: 'Social Trend', icon: '🌐', color: 'text-coral' },
  ];

  return (
    <div className="terminal-card bg-bg1/40 border-white/5 space-y-6">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-[10px] font-mono font-bold text-white/40 tracking-[0.2em] uppercase">Conflux Weights</h3>
        <span className="text-[9px] font-mono text-amber/60">SIMULATION MODE</span>
      </div>
      
      <div className="space-y-5">
        {controls.map((ctrl) => (
          <div key={ctrl.key} className="space-y-2">
            <div className="flex justify-between items-center text-[11px] font-medium">
              <div className="flex items-center gap-2">
                <span className={ctrl.color}>{ctrl.icon}</span>
                <span className="text-white/60">{ctrl.label}</span>
              </div>
              <span className="font-mono text-white/40">{(weights[ctrl.key] * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={weights[ctrl.key]}
              onChange={(e) => onWeightChange(ctrl.key, parseFloat(e.target.value))}
              className="w-full h-1 bg-white/5 rounded-lg appearance-none cursor-pointer accent-amber hover:accent-amber/80 transition-all"
            />
          </div>
        ))}
      </div>

      <div className="pt-4 border-t border-white/5">
         <p className="text-[9px] text-white/20 italic leading-relaxed uppercase tracking-tighter">
           Adjusting weights will re-calculate the conflux score for all 48 teams in real-time.
         </p>
      </div>
    </div>
  );
};

export default IntelligenceControls;
