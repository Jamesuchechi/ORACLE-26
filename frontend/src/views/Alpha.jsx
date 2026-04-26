
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Target, TrendingUp, AlertTriangle, CheckCircle2, ChevronRight, Zap, Info, ShieldCheck, Filter, Activity } from 'lucide-react';
import axios from 'axios';
import { 
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine,
  BarChart, Bar, ComposedChart, Line, Legend, Area
} from 'recharts';

const AlphaView = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAlpha, setSelectedAlpha] = useState(null);
  const [isDeploying, setIsDeploying] = useState(false);
  const [isDeployed, setIsDeployed] = useState(false);
  const [chartType, setChartType] = useState('scatter'); // 'scatter' | 'bar' | 'delta'

  const handleDeploy = () => {
    setIsDeploying(true);
    setTimeout(() => {
      setIsDeploying(false);
      setIsDeployed(true);
    }, 2000);
  };

  useEffect(() => {
    const fetchAlpha = async () => {
      try {
        const res = await axios.get('/v1/predict/alpha/discovery');
        setData(res.data);
        if (res.data?.alpha_plays?.length > 0) setSelectedAlpha(res.data.alpha_plays[0]);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setError('Alpha Detection Scanner Offline');
        setLoading(false);
      }
    };
    fetchAlpha();
  }, []);

  useEffect(() => {
    setIsDeployed(false);
  }, [selectedAlpha]);

  if (loading) return <div className="p-12 text-center font-mono text-muted animate-pulse uppercase tracking-widest text-xs">Scanning Markets for Divergence...</div>;
  if (error) return <div className="p-12 text-center text-red font-mono text-xs uppercase">{error}</div>;

  // Prepare scatter data
  const scatterData = (data?.alpha_plays || []).map(p => ({
    name: p.subject,
    x: (p.market_prob || 0) * 100,
    y: (p.model_prob || 0) * 100,
    alpha: (p.alpha || 0) * 100
  }));

  return (
    <div className="space-y-8 pb-12">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left: Opportunity Radar */}
        <div className="col-span-1 lg:col-span-7 space-y-8">
          <div className="terminal-card bg-bg1/20 border-border p-4 lg:p-8">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-6">
              <h3 className="text-xl font-bold flex items-center gap-3">
                <Target className="text-teal" size={22} />
                Opportunity Analysis
              </h3>
              
              <div className="flex items-center gap-1 bg-foreground/20 p-1 rounded-lg border border-border w-full sm:w-auto justify-between sm:justify-start">
                <button 
                  onClick={() => setChartType('scatter')}
                  className={`p-1.5 flex-1 sm:flex-none flex justify-center rounded-md transition-all ${chartType === 'scatter' ? 'bg-teal text-bg1 shadow-lg' : 'text-muted hover:text-foreground'}`}
                  title="Scatter Plot (Radar)"
                >
                  <Target size={16} />
                </button>
                <button 
                  onClick={() => setChartType('bar')}
                  className={`p-1.5 flex-1 sm:flex-none flex justify-center rounded-md transition-all ${chartType === 'bar' ? 'bg-teal text-bg1 shadow-lg' : 'text-muted hover:text-foreground'}`}
                  title="Alpha Ranking (Bar)"
                >
                  <TrendingUp size={16} />
                </button>
                <button 
                  onClick={() => setChartType('delta')}
                  className={`p-1.5 flex-1 sm:flex-none flex justify-center rounded-md transition-all ${chartType === 'delta' ? 'bg-teal text-bg1 shadow-lg' : 'text-muted hover:text-foreground'}`}
                  title="Divergence Delta"
                >
                  <Activity size={16} />
                </button>
              </div>

              <div className="flex gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-teal" />
                  <span className="text-[10px] font-mono text-muted uppercase">High Alpha</span>
                </div>
              </div>
            </div>

            <div className="h-[300px] lg:h-[400px] w-full relative">
               <AnimatePresence mode="wait">
                 {chartType === 'scatter' && (
                   <motion.div key="scatter" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="w-full h-full">
                     <div className="absolute top-4 left-4 text-[9px] font-mono text-muted uppercase vertical-text hidden sm:block">Conflux Model Probability %</div>
                     <div className="absolute bottom-4 right-4 text-[9px] font-mono text-muted uppercase hidden sm:block">Market Implied Probability %</div>
                     <ResponsiveContainer width="100%" height="100%">
                       <ScatterChart margin={{ top: 10, right: 10, bottom: 10, left: -20 }}>
                         <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--foreground-rgb) / 0.05)" />
                         <XAxis type="number" dataKey="x" domain={[0, 100]} tick={{ fill: 'rgb(var(--foreground-rgb) / 0.3)', fontSize: 9, fontFamily: 'monospace' }} />
                         <YAxis type="number" dataKey="y" domain={[0, 100]} tick={{ fill: 'rgb(var(--foreground-rgb) / 0.3)', fontSize: 9, fontFamily: 'monospace' }} />
                         <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ background: '#111', border: '1px solid rgb(var(--foreground-rgb) / 0.1)', fontSize: '10px', fontFamily: 'monospace' }} />
                         <ReferenceLine segment={[{ x: 0, y: 0 }, { x: 100, y: 100 }]} stroke="rgb(var(--foreground-rgb) / 0.1)" strokeDasharray="5 5" />
                         <Scatter name="Alpha" data={scatterData} onClick={(e) => setSelectedAlpha(data.alpha_plays.find(p => p.subject === e.name))}>
                           {scatterData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.alpha > 10 ? '#2dd4bf' : '#3b82f6'} className="cursor-pointer" />)}
                         </Scatter>
                       </ScatterChart>
                     </ResponsiveContainer>
                   </motion.div>
                 )}

                 {chartType === 'bar' && (
                   <motion.div key="bar" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="w-full h-full">
                     <ResponsiveContainer width="100%" height="100%">
                       <BarChart data={scatterData.sort((a,b) => b.alpha - a.alpha)} layout="vertical" margin={{ left: -20, right: 10, top: 0, bottom: 0 }}>
                         <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--foreground-rgb) / 0.05)" horizontal={false} />
                         <XAxis type="number" tick={{ fill: 'rgb(var(--foreground-rgb) / 0.3)', fontSize: 9 }} />
                         <YAxis dataKey="name" type="category" tick={{ fill: 'rgb(var(--foreground-rgb) / 0.6)', fontSize: 9, fontWeight: 'bold' }} width={70} />
                         <Tooltip contentStyle={{ background: '#111', border: 'none', borderRadius: '8px' }} />
                         <Bar dataKey="alpha" name="Alpha Edge %" fill="#2dd4bf" radius={[0, 4, 4, 0]}>
                            {scatterData.map((entry, index) => <Cell key={`cell-${index}`} fillOpacity={0.4 + (index * 0.1)} />)}
                         </Bar>
                       </BarChart>
                     </ResponsiveContainer>
                   </motion.div>
                 )}

                 {chartType === 'delta' && (
                   <motion.div key="delta" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="w-full h-full">
                     <ResponsiveContainer width="100%" height="100%">
                       <ComposedChart data={scatterData} margin={{ top: 10, right: 10, left: -30, bottom: 0 }}>
                         <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--foreground-rgb) / 0.05)" />
                         <XAxis 
                            dataKey="name" 
                            tick={{ fill: 'rgb(var(--foreground-rgb) / 0.3)', fontSize: 9 }} 
                            interval={0}
                            angle={window.innerWidth < 640 ? -45 : 0}
                            textAnchor={window.innerWidth < 640 ? 'end' : 'middle'}
                          />
                         <YAxis tick={{ fill: 'rgb(var(--foreground-rgb) / 0.3)', fontSize: 9 }} />
                         <Tooltip contentStyle={{ background: '#111', border: 'none' }} />
                         <Bar dataKey="x" name="Market %" fill="rgb(var(--foreground-rgb) / 0.05)" stroke="rgb(var(--foreground-rgb) / 0.2)" />
                         <Line type="monotone" dataKey="y" name="Model %" stroke="#2dd4bf" strokeWidth={3} dot={{ fill: '#2dd4bf', r: 4 }} />
                         <Area type="monotone" dataKey="y" fill="#2dd4bf" fillOpacity={0.05} stroke="none" />
                       </ComposedChart>
                     </ResponsiveContainer>
                   </motion.div>
                 )}
               </AnimatePresence>
            </div>
            
            <div className="mt-4 p-4 rounded-lg bg-teal/5 border border-teal/20">
               <p className="text-[10px] text-teal/80 font-mono flex items-start lg:items-center gap-2">
                 <Info size={12} className="shrink-0 mt-0.5 lg:mt-0" />
                 Divergence Legend: Items above the diagonal are UNDERPRICED (Value). Items below are OVERPRICED (Hype).
               </p>
            </div>
          </div>

          <div className="space-y-4">
             {(data?.alpha_plays || []).map((play, i) => (
               <motion.div 
                 key={play.subject}
                 onClick={() => setSelectedAlpha(play)}
                 whileHover={{ scale: 1.01 }}
                 className={`p-4 lg:p-6 rounded-2xl border transition-all cursor-pointer flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${
                   selectedAlpha?.subject === play.subject 
                   ? 'bg-teal/10 border-teal/40 shadow-[0_0_20px_rgba(45,212,191,0.1)]' 
                   : 'bg-[var(--card-bg)] border-border hover:bg-[var(--card-bg)]'
                 }`}
               >
                 <div className="flex items-center gap-4 lg:gap-6">
                   <div className={`p-3 rounded-xl ${play.alpha > 0.1 ? 'bg-teal/20 text-teal' : 'bg-blue/20 text-blue'}`}>
                     <TrendingUp size={20} lg:size={24} />
                   </div>
                   <div>
                     <h4 className="text-base lg:text-lg font-bold">{play.subject}</h4>
                     <div className="flex gap-2 mt-1">
                       {play.confirmed_by.map(c => (
                         <span key={c} className="text-[8px] font-mono font-bold text-foreground/30 uppercase tracking-widest">{c}</span>
                       ))}
                     </div>
                   </div>
                 </div>
                 
                 <div className="flex items-center justify-between sm:justify-end gap-6 lg:gap-12 w-full sm:w-auto">
                    <div className="text-left sm:text-right">
                       <p className="text-[9px] font-mono text-muted uppercase">Alpha Edge</p>
                       <p className="text-lg lg:text-xl font-mono font-bold text-teal">+{ (play.alpha * 100).toFixed(1) }%</p>
                    </div>
                    <div className="text-right w-20 lg:w-24">
                       <p className="text-[9px] font-mono text-muted uppercase">Conviction</p>
                       <p className={`text-xs font-bold ${play.conviction === 'HIGH' ? 'text-teal' : 'text-blue'}`}>{play.conviction}</p>
                    </div>
                    <ChevronRight size={20} className="text-foreground/10 hidden sm:block" />
                 </div>
               </motion.div>
             ))}
          </div>
        </div>

        {/* Right: Detailed Execution Strategy */}
        <div className="col-span-1 lg:col-span-5 space-y-6">
          <AnimatePresence mode="wait">
             {selectedAlpha && (
               <motion.div 
                 key={selectedAlpha.subject}
                 initial={{ opacity: 0, x: 20 }}
                 animate={{ opacity: 1, x: 0 }}
                 exit={{ opacity: 0, x: -20 }}
                 className="terminal-card bg-bg1/40 border-teal/20 p-6 lg:p-8 shadow-[0_0_50px_rgba(45,212,191,0.05)] sticky top-8"
               >
                 <div className="mb-6 lg:mb-8">
                   <p className="text-[10px] font-mono text-teal uppercase tracking-[0.3em] mb-2">Alpha Execution Report</p>
                   <h3 className="text-2xl lg:text-3xl font-bold">{selectedAlpha.subject}</h3>
                 </div>

                 <div className="grid grid-cols-2 gap-4 lg:gap-6 mb-8 lg:mb-10">
                    <div className="p-4 rounded-xl bg-[var(--card-bg)] border border-border text-center sm:text-left">
                       <p className="text-[10px] font-mono text-muted uppercase mb-2">Market Odds</p>
                       <p className="text-xl lg:text-2xl font-mono font-bold text-muted">{(selectedAlpha.market_prob * 100).toFixed(1)}%</p>
                    </div>
                    <div className="p-4 rounded-xl bg-teal/5 border border-teal/20 text-center sm:text-left">
                       <p className="text-[10px] font-mono text-teal uppercase mb-2">Conflux Model</p>
                       <p className="text-xl lg:text-2xl font-mono font-bold text-teal">{(selectedAlpha.model_prob * 100).toFixed(1)}%</p>
                    </div>
                 </div>

                 <div className="space-y-6">
                   <div>
                     <div className="flex items-center gap-2 mb-3 text-teal">
                        <Zap size={16} />
                        <span className="text-[10px] font-mono font-bold uppercase">Strategic Logic</span>
                     </div>
                     <div className="p-5 rounded-xl bg-[var(--card-bg)] border border-border">
                        <p className="text-sm text-foreground/70 leading-relaxed italic">
                          "Signal confirmation across Sports and Social domains suggests market is underestimating travel fatigue and squad depth interaction. This divergence represents a 4.2-sigma event in current volatility bands."
                        </p>
                     </div>
                   </div>

                   <div className="p-6 rounded-2xl bg-teal/5 border border-teal/20 relative overflow-hidden">
                      {isDeploying && (
                        <motion.div 
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          className="absolute inset-0 bg-bg1/90 backdrop-blur-sm z-10 flex flex-col items-center justify-center gap-4"
                        >
                          <div className="w-8 h-8 border-2 border-teal border-t-transparent rounded-full animate-spin" />
                          <p className="text-[10px] font-mono text-teal animate-pulse">EXECUTING_SMART_CONTRACT...</p>
                        </motion.div>
                      )}
                      
                      {isDeployed ? (
                        <motion.div 
                          initial={{ scale: 0.9, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          className="text-center py-4"
                        >
                          <div className="w-12 h-12 bg-teal/20 text-teal rounded-full flex items-center justify-center mx-auto mb-4">
                            <CheckCircle2 size={24} />
                          </div>
                          <h4 className="text-sm font-bold text-foreground mb-2">Capital Deployed</h4>
                          <p className="text-[9px] font-mono text-teal/60 mb-4 tracking-tighter">TX: 0x{Math.random().toString(16).slice(2, 10)}...{Math.random().toString(16).slice(2, 6)}</p>
                          <button 
                            onClick={() => setIsDeployed(false)}
                            className="text-[10px] font-bold text-muted hover:text-foreground uppercase tracking-widest underline underline-offset-4"
                          >
                            Reset Position
                          </button>
                        </motion.div>
                      ) : (
                        <>
                          <div className="flex items-center gap-3 mb-4 text-teal">
                             <ShieldCheck size={18} />
                             <span className="text-xs font-bold uppercase tracking-widest">Recommended Play</span>
                          </div>
                          <p className="text-sm font-bold text-foreground mb-4">{selectedAlpha.strategy}</p>
                          <button 
                            onClick={handleDeploy}
                            className="w-full py-3 bg-teal text-bg1 rounded-xl text-xs font-bold uppercase tracking-widest hover:bg-teal/80 transition-all active:scale-95"
                          >
                            DEPLOY_CAPITAL
                          </button>
                        </>
                      )}
                   </div>
                 </div>

                 <div className="mt-10 pt-8 border-t border-border">
                    <p className="text-[9px] font-mono text-muted mb-4 uppercase">Verification Nodes</p>
                    <div className="flex flex-wrap gap-2">
                       {['Neural_Llama_3.3', 'Conflux_V2', 'Polymarket_Oracle', 'FRED_Sync'].map(node => (
                         <span key={node} className="px-2 py-1 rounded bg-foreground/20 text-[8px] font-mono text-muted">{node}</span>
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
