import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const Leaderboard = ({ rankings, loading }) => {
  if (loading && rankings.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-white/20 font-mono text-xs uppercase tracking-[0.3em]">
        <div className="w-12 h-12 border-2 border-amber/20 border-t-amber rounded-full animate-spin mb-4" />
        Syncing Neural Signals...
      </div>
    );
  }

  return (
    <div className="overflow-hidden">
      <div className="grid grid-cols-12 px-4 py-2 text-[9px] font-mono text-white/20 uppercase tracking-widest border-b border-white/5">
        <div className="col-span-1">Rank</div>
        <div className="col-span-4">Subject / Team</div>
        <div className="col-span-5">Signal Breakdown</div>
        <div className="col-span-2 text-right">Conflux ◈</div>
      </div>
      
      <div className="mt-2 space-y-1 relative">
        <AnimatePresence mode="popLayout">
          {rankings.map((team, index) => (
            <motion.div
              key={team.subject}
              layout
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ 
                type: "spring", 
                stiffness: 500, 
                damping: 30, 
                mass: 1,
                opacity: { duration: 0.2 }
              }}
              className={`grid grid-cols-12 items-center px-4 py-3 rounded-lg border border-transparent transition-colors hover:bg-white/[0.03] hover:border-white/5 group`}
            >
              <div className="col-span-1 font-mono text-[10px] text-white/30">
                {String(index + 1).padStart(2, '0')}
              </div>
              
              <div className="col-span-4 flex items-center gap-3">
                <span className="text-lg">{team.flag || '🏳️'}</span>
                <div>
                  <h4 className="text-xs font-bold tracking-wide group-hover:text-amber transition-colors">{team.subject}</h4>
                  <p className="text-[9px] font-mono text-white/20 uppercase">Confidence: {team.confidence}</p>
                </div>
              </div>
              
              <div className="col-span-5 flex items-center gap-1.5">
                <SignalDot val={team.sports} color="bg-blue" label="S" />
                <SignalDot val={team.markets} color="bg-amber" label="M" />
                <SignalDot val={team.finance} color="bg-teal" label="E" />
                <SignalDot val={team.climate} color="bg-red" label="C" />
                <SignalDot val={team.social} color="bg-coral" label="T" />
              </div>
              
              <div className="col-span-2 text-right">
                <span className="font-mono text-sm font-bold text-amber">
                  {team.conflux_score.toFixed(3)}
                </span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};

const SignalDot = ({ val, color, label }) => (
  <div className="relative group/dot">
    <div className="w-1.5 h-1.5 rounded-full bg-white/5 overflow-hidden">
      <div 
        className={`h-full ${color}`} 
        style={{ width: `${val * 100}%` }}
      />
    </div>
    <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-bg3 text-[8px] font-mono px-1.5 py-0.5 rounded border border-white/10 opacity-0 group-hover/dot:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
      {label}: {(val * 100).toFixed(0)}%
    </div>
  </div>
);

export default Leaderboard;
