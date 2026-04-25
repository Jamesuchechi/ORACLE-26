
import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, TrendingUp, Zap, ArrowRight, ShieldCheck } from 'lucide-react';

const DivergenceAlert = ({ alpha }) => {
  const items = alpha?.value || [];
  
  if (items.length === 0) return null;

  return (
    <div className="mb-10">
      <div className="flex items-center gap-3 mb-6">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-red/10 border border-red/20 text-red text-[10px] font-mono font-bold uppercase tracking-widest animate-pulse">
          <AlertTriangle size={12} />
          Critical Market Divergence Detected
        </div>
        <div className="h-px flex-1 bg-white/5" />
        <div className="text-[10px] font-mono text-white/20 uppercase tracking-widest">
          Scanning 48 Entities
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {items.slice(0, 5).map((item, index) => {
          const name = item.subject || item.description || "Unknown Asset";
          const gap = (item.alpha_gap || 0) * 100;
          
          return (
            <motion.div
              key={`${name}-${index}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="group relative terminal-card bg-bg1/20 border-white/5 p-5 hover:border-amber/30 transition-all cursor-pointer overflow-hidden"
            >
              {/* Decorative Accent */}
              <div className="absolute top-0 right-0 w-24 h-24 bg-amber/5 blur-3xl -mr-12 -mt-12 group-hover:bg-amber/10 transition-colors" />
              
              <div className="relative z-10">
                <div className="flex justify-between items-start mb-4">
                  <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-amber group-hover:scale-110 transition-transform">
                    <Zap size={16} />
                  </div>
                  <div className="px-2 py-1 rounded bg-teal/10 border border-teal/20 text-teal text-[9px] font-mono font-bold">
                    VALUE
                  </div>
                </div>

                <h4 className="text-sm font-bold mb-1 truncate group-hover:text-amber transition-colors">
                  {name}
                </h4>
                <p className="text-[10px] text-white/30 font-mono mb-4 uppercase tracking-tighter">
                  Alpha Gap: <span className="text-teal">+{gap.toFixed(1)}pp</span>
                </p>

                <div className="space-y-3 pt-4 border-t border-white/5">
                  <div className="flex justify-between items-center text-[10px] font-mono">
                    <span className="text-white/20 uppercase">Model</span>
                    <span className="text-white/80">{(item.conflux_score * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between items-center text-[10px] font-mono">
                    <span className="text-white/20 uppercase">Market</span>
                    <span className="text-white/40">{(item.market_prob * 100 || item.markets * 100 || 0).toFixed(1)}%</span>
                  </div>
                </div>

                {/* AI Reasoning Preview */}
                <div className="mt-4 flex items-center gap-2 text-white/20 group-hover:text-amber/60 transition-colors">
                  <span className="text-[8px] font-mono uppercase tracking-widest">View Intel</span>
                  <ArrowRight size={10} />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default DivergenceAlert;
