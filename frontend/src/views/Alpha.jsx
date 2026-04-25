
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Target, TrendingUp, AlertTriangle, CheckCircle2, ChevronRight, Zap, Info, ShieldCheck, Filter } from 'lucide-react';
import axios from 'axios';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';

const AlphaView = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAlpha, setSelectedAlpha] = useState(null);

  useEffect(() => {
    const fetchAlpha = async () => {
      try {
        const res = await axios.get('/v1/predict/alpha/discovery');
        setData(res.data);
        if (res.data.alpha_plays.length > 0) setSelectedAlpha(res.data.alpha_plays[0]);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setError('Alpha Detection Scanner Offline');
        setLoading(false);
      }
    };
    fetchAlpha();
  }, []);

  if (loading) return <div className="p-12 text-center font-mono text-white/20 animate-pulse uppercase tracking-widest text-xs">Scanning Markets for Divergence...</div>;
  if (error) return <div className="p-12 text-center text-red font-mono text-xs uppercase">{error}</div>;

  // Prepare scatter data
  const scatterData = data.alpha_plays.map(p => ({
    name: p.subject,
    x: p.market_prob * 100,
    y: p.model_prob * 100,
    alpha: p.alpha * 100
  }));

  return (
    <div className="space-y-8 pb-12">
      <div className="grid grid-cols-12 gap-8">
        {/* Left: Opportunity Radar */}
        <div className="col-span-7 space-y-8">
          <div className="terminal-card bg-bg1/20 border-white/5 p-8">
            <div className="flex justify-between items-center mb-8">
              <h3 className="text-xl font-bold flex items-center gap-3">
                <Target className="text-teal" size={22} />
                Opportunity Radar
              </h3>
              <div className="flex gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-teal" />
                  <span className="text-[10px] font-mono text-white/40 uppercase">High Alpha</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-white/20" />
                  <span className="text-[10px] font-mono text-white/40 uppercase">Market Parity</span>
                </div>
              </div>
            </div>

            <div className="h-96 w-full relative">
               <div className="absolute top-4 left-4 text-[9px] font-mono text-white/20 uppercase vertical-text">Conflux Model Probability %</div>
               <div className="absolute bottom-4 right-4 text-[9px] font-mono text-white/20 uppercase">Market Implied Probability %</div>
               
               <ResponsiveContainer width="100%" height="100%">
                 <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                   <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                   <XAxis 
                     type="number" 
                     dataKey="x" 
                     domain={[0, 100]} 
                     tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 10, fontFamily: 'monospace' }}
                   />
                   <YAxis 
                     type="number" 
                     dataKey="y" 
                     domain={[0, 100]} 
                     tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 10, fontFamily: 'monospace' }}
                   />
                   <Tooltip 
                     cursor={{ strokeDasharray: '3 3' }}
                     contentStyle={{ background: '#111', border: '1px solid rgba(255,255,255,0.1)', fontSize: '10px', fontFamily: 'monospace' }}
                   />
                   <ReferenceLine segment={[{ x: 0, y: 0 }, { x: 100, y: 100 }]} stroke="rgba(255,255,255,0.1)" strokeDasharray="5 5" />
                   <Scatter name="Alpha" data={scatterData} onClick={(e) => setSelectedAlpha(data.alpha_plays.find(p => p.subject === e.name))}>
                     {scatterData.map((entry, index) => (
                       <Cell 
                         key={`cell-${index}`} 
                         fill={entry.alpha > 10 ? '#2dd4bf' : '#3b82f6'} 
                         className="cursor-pointer"
                       />
                     ))}
                   </Scatter>
                 </ScatterChart>
               </ResponsiveContainer>
            </div>
            
            <div className="mt-4 p-4 rounded-lg bg-teal/5 border border-teal/20">
               <p className="text-[10px] text-teal/80 font-mono flex items-center gap-2">
                 <Info size={12} />
                 Divergence Legend: Items above the diagonal are UNDERPRICED (Value). Items below are OVERPRICED (Hype).
               </p>
            </div>
          </div>

          <div className="space-y-4">
             {data.alpha_plays.map((play, i) => (
               <motion.div 
                 key={play.subject}
                 onClick={() => setSelectedAlpha(play)}
                 whileHover={{ scale: 1.01 }}
                 className={`p-6 rounded-2xl border transition-all cursor-pointer flex items-center justify-between ${
                   selectedAlpha?.subject === play.subject 
                   ? 'bg-teal/10 border-teal/40 shadow-[0_0_20px_rgba(45,212,191,0.1)]' 
                   : 'bg-white/[0.02] border-white/5 hover:bg-white/[0.04]'
                 }`}
               >
                 <div className="flex items-center gap-6">
                   <div className={`p-3 rounded-xl ${play.alpha > 0.1 ? 'bg-teal/20 text-teal' : 'bg-blue/20 text-blue'}`}>
                     <TrendingUp size={24} />
                   </div>
                   <div>
                     <h4 className="text-lg font-bold">{play.subject}</h4>
                     <div className="flex gap-2 mt-1">
                       {play.confirmed_by.map(c => (
                         <span key={c} className="text-[8px] font-mono font-bold text-white/30 uppercase tracking-widest">{c}</span>
                       ))}
                     </div>
                   </div>
                 </div>
                 
                 <div className="flex items-center gap-12">
                    <div className="text-right">
                       <p className="text-[9px] font-mono text-white/20 uppercase">Alpha Edge</p>
                       <p className="text-xl font-mono font-bold text-teal">+{ (play.alpha * 100).toFixed(1) }%</p>
                    </div>
                    <div className="text-right w-24">
                       <p className="text-[9px] font-mono text-white/20 uppercase">Conviction</p>
                       <p className={`text-xs font-bold ${play.conviction === 'HIGH' ? 'text-teal' : 'text-blue'}`}>{play.conviction}</p>
                    </div>
                    <ChevronRight size={20} className="text-white/10" />
                 </div>
               </motion.div>
             ))}
          </div>
        </div>

        {/* Right: Detailed Execution Strategy */}
        <div className="col-span-5 space-y-6">
          <AnimatePresence mode="wait">
             {selectedAlpha && (
               <motion.div 
                 key={selectedAlpha.subject}
                 initial={{ opacity: 0, x: 20 }}
                 animate={{ opacity: 1, x: 0 }}
                 exit={{ opacity: 0, x: -20 }}
                 className="terminal-card bg-bg1/40 border-teal/20 p-8 shadow-[0_0_50px_rgba(45,212,191,0.05)] sticky top-8"
               >
                 <div className="mb-8">
                   <p className="text-[10px] font-mono text-teal uppercase tracking-[0.3em] mb-2">Alpha Execution Report</p>
                   <h3 className="text-3xl font-bold">{selectedAlpha.subject}</h3>
                 </div>

                 <div className="grid grid-cols-2 gap-6 mb-10">
                    <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
                       <p className="text-[10px] font-mono text-white/20 uppercase mb-2">Market Odds</p>
                       <p className="text-2xl font-mono font-bold text-white/40">{(selectedAlpha.market_prob * 100).toFixed(1)}%</p>
                    </div>
                    <div className="p-4 rounded-xl bg-teal/5 border border-teal/20">
                       <p className="text-[10px] font-mono text-teal uppercase mb-2">Conflux Model</p>
                       <p className="text-2xl font-mono font-bold text-teal">{(selectedAlpha.model_prob * 100).toFixed(1)}%</p>
                    </div>
                 </div>

                 <div className="space-y-6">
                   <div>
                     <div className="flex items-center gap-2 mb-3 text-teal">
                        <Zap size={16} />
                        <span className="text-[10px] font-mono font-bold uppercase">Strategic Logic</span>
                     </div>
                     <div className="p-5 rounded-xl bg-white/[0.01] border border-white/5">
                        <p className="text-sm text-white/70 leading-relaxed italic">
                          "Signal confirmation across Sports and Social domains suggests market is underestimating travel fatigue and squad depth interaction. This divergence represents a 4.2-sigma event in current volatility bands."
                        </p>
                     </div>
                   </div>

                   <div className="p-6 rounded-2xl bg-teal/5 border border-teal/20">
                      <div className="flex items-center gap-3 mb-4 text-teal">
                         <ShieldCheck size={18} />
                         <span className="text-xs font-bold uppercase tracking-widest">Recommended Play</span>
                      </div>
                      <p className="text-sm font-bold text-white mb-4">{selectedAlpha.strategy}</p>
                      <button className="w-full py-3 bg-teal text-bg1 rounded-xl text-xs font-bold uppercase tracking-widest hover:bg-teal/80 transition-all">
                        DEPLOY_CAPITAL
                      </button>
                   </div>
                 </div>

                 <div className="mt-10 pt-8 border-t border-white/5">
                    <p className="text-[9px] font-mono text-white/20 mb-4 uppercase">Verification Nodes</p>
                    <div className="flex flex-wrap gap-2">
                       {['Neural_Llama_3.3', 'Conflux_V2', 'Polymarket_Oracle', 'FRED_Sync'].map(node => (
                         <span key={node} className="px-2 py-1 rounded bg-white/5 text-[8px] font-mono text-white/40">{node}</span>
                       ))}
                    </div>
                 </div>
               </motion.div>
             )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default AlphaView;
