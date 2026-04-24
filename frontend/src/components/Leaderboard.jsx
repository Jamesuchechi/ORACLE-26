import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getFlagUrl } from '../utils/flags';

const Leaderboard = ({ rankings, loading, onTeamClick }) => {
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
        <div className="col-span-5">Intelligence Fingerprint</div>
        <div className="col-span-2 text-right">Conflux Score</div>
      </div>
      
      <div className="mt-4 space-y-1 relative">
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
              className={`grid grid-cols-12 items-center px-4 py-4 rounded-xl border border-transparent transition-all hover:bg-white/[0.04] hover:border-white/10 group cursor-pointer relative overflow-hidden`}
              onClick={() => onTeamClick(team)}
            >
              <div className="col-span-1 font-mono text-[11px] text-white/20 font-bold">
                {String(index + 1).padStart(2, '0')}
              </div>
              
              <div className="col-span-4 flex items-center gap-4">
                <div className="relative">
                  <img 
                    src={getFlagUrl(team.subject)} 
                    alt={team.subject} 
                    className="w-8 h-5 object-cover rounded-sm shadow-lg border border-white/10 group-hover:border-amber/40 transition-colors"
                  />
                </div>
                <div>
                  <h4 className="text-xs font-bold tracking-wider group-hover:text-amber transition-colors text-white/80">{team.subject}</h4>
                  <p className="text-[9px] font-mono text-white/20 uppercase tracking-tighter">Confidence: <span className={team.confidence === 'high' ? 'text-teal' : 'text-amber/50'}>{team.confidence}</span></p>
                </div>
              </div>
              
              <div className="col-span-5 flex items-center gap-1">
                <SignalBar val={team.sports} color="bg-blue" label="S" />
                <SignalBar val={team.markets} color="bg-amber" label="M" />
                <SignalBar val={team.finance} color="bg-teal" label="E" />
                <SignalBar val={team.climate} color="bg-red" label="C" />
                <SignalBar val={team.social} color="bg-coral" label="T" />
              </div>

              
              <div className="col-span-2 text-right">
                <span className="font-mono text-sm font-black text-amber drop-shadow-[0_0_8px_rgba(245,158,11,0.3)]">
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

const SignalBar = ({ val, color, label }) => (
  <div className="flex-1 group/bar relative">
    <div className="h-1 bg-white/5 rounded-full overflow-hidden">
      <motion.div 
        initial={{ width: 0 }}
        animate={{ width: `${(val || 0) * 100}%` }}
        className={`h-full ${color} opacity-60 group-hover/bar:opacity-100 transition-opacity`} 
      />
    </div>
    <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-bg1 text-[8px] font-mono px-2 py-0.5 rounded border border-white/10 opacity-0 group-hover/bar:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
      {label}: {((val || 0) * 100).toFixed(0)}%
    </div>
  </div>
);



export default Leaderboard;
