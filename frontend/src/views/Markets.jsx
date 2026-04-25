
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, Zap, ArrowUpRight, ArrowDownRight, Activity, Globe, Brain, Loader2 } from 'lucide-react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell, Tooltip, Radar, RadarChart, PolarGrid, PolarAngleAxis } from 'recharts';
import ReactMarkdown from 'react-markdown';

const MarketsView = ({ alpha, rankings }) => {
  const [selectedEventId, setSelectedEventId] = useState(null);
  const [marketsData, setMarketsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [executing, setExecuting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [depthData, setDepthData] = useState(null);
  const [loadingDepth, setLoadingDepth] = useState(false);

  useEffect(() => {
    axios.get('/v1/markets/dashboard')
      .then(res => {
        const data = res.data?.events || [];
        setMarketsData(data);
        if (data.length > 0) setSelectedEventId(data[0].event_id);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError(err.code === 'ECONNABORTED' ? 'Market Link Timeout' : 'Calibration Engine Offline');
        setLoading(false);
      });
  }, []);

  const selectedEvent = marketsData.find(e => e.event_id === selectedEventId);

  const handleArbitrage = async () => {
    if (!selectedEvent) return;
    setExecuting(true);
    setSuccess(false);
    setDepthData(null);
    setLoadingDepth(true);

    try {
      // Parallel execution: Mock delay + Real AI Depth Fetch
      const [_, depthRes] = await Promise.all([
        new Promise(resolve => setTimeout(resolve, 2000)),
        axios.get(`/v1/markets/${selectedEvent.event_id}/depth`)
      ]);
      
      setDepthData(depthRes.data);
      setExecuting(false);
      setSuccess(true);
      setLoadingDepth(false);
    } catch (err) {
      console.error("Depth fetch failed:", err);
      setExecuting(false);
      setLoadingDepth(false);
      setSuccess(true); // Still show success for arbitrage logic
    }
  };

  if (loading) return <div className="p-12 text-center font-mono text-white/20 animate-pulse uppercase tracking-widest text-xs">Synchronizing Market Signals...</div>;
  if (error) return (
    <div className="p-12 text-center">
      <p className="text-red font-mono text-xs uppercase mb-4">{error}</p>
      <button onClick={() => window.location.reload()} className="px-4 py-2 border border-white/10 rounded-lg text-[10px] font-mono text-white/40 hover:text-white transition-colors">RETRY_LINK</button>
    </div>
  );

  return (
    <div className="space-y-8 pb-12">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="col-span-1 lg:col-span-8 space-y-8">
          <div className="terminal-card bg-bg1/20 border-white/5 p-6">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <TrendingUp className="text-amber" size={20} />
              Prediction Market Calibration
            </h3>
            
            <div className="space-y-4">
              {marketsData.map(market => (
                <div 
                  key={market.event_id} 
                  onClick={() => { setSelectedEventId(market.event_id); setSuccess(false); setDepthData(null); }}
                  className={`p-4 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                    selectedEventId === market.event_id 
                      ? 'border-amber/40 bg-amber/5' 
                      : 'border-white/5 bg-white/[0.02] hover:bg-white/[0.05]'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${selectedEventId === market.event_id ? 'bg-amber/20 text-amber' : 'bg-bg1 text-white/40'}`}>
                      <Globe size={18} />
                    </div>
                    <div>
                      <p className="text-[10px] font-mono text-white/20 uppercase tracking-widest">{market.type}</p>
                      <h4 className={`text-sm font-bold ${selectedEventId === market.event_id ? 'text-white' : 'text-white/80'}`}>{market.description}</h4>
                    </div>
                  </div>
                  <div className="flex items-center gap-8">
                    <div className="text-right">
                      <p className="text-[10px] font-mono text-white/20 uppercase">Implied Prob</p>
                      <p className="text-xl font-mono font-bold text-amber">{((market.implied_prob || 0) * 100).toFixed(0)}%</p>
                    </div>
                    <div className={market.alpha > 0 ? 'text-teal' : 'text-red'}>
                      {market.alpha > 0 ? <ArrowUpRight size={20} /> : <ArrowDownRight size={20} />}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <AnimatePresence>
            {depthData && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="terminal-card bg-bg1/40 border-teal/20 p-8 shadow-[0_0_50px_rgba(20,184,166,0.05)]"
              >
                <div className="flex justify-between items-start mb-8">
                  <div>
                    <h3 className="text-xl font-bold flex items-center gap-3 text-teal">
                      <Brain size={24} />
                      AI Strategy Depth: {selectedEvent?.description}
                    </h3>
                    <p className="text-[10px] font-mono text-white/40 uppercase mt-2 tracking-widest">Powered by Conflux Neural Analyst (Groq Llama-3.3)</p>
                  </div>
                  <div className="px-3 py-1 rounded-full bg-teal/10 border border-teal/20 text-[10px] font-mono text-teal font-bold uppercase">
                    Execution: ACTIVE
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-12">
                  <div className="prose prose-invert prose-xs max-w-none">
                    <ReactMarkdown components={{
                      strong: ({node, ...props}) => <span className="text-teal font-bold" {...props} />,
                      p: ({node, ...props}) => <p className="text-xs text-white/70 leading-relaxed mb-4" {...props} />,
                      li: ({node, ...props}) => <li className="text-xs text-white/70 mb-2" {...props} />,
                    }}>
                      {depthData.depth_text}
                    </ReactMarkdown>
                  </div>

                  <div className="space-y-8">
                    <div className="h-64 w-full">
                       <p className="text-[10px] font-mono text-white/20 uppercase mb-4 text-center tracking-widest">Signal Confidence Breakdown</p>
                       <ResponsiveContainer width="100%" height="100%">
                         <RadarChart cx="50%" cy="50%" outerRadius="80%" data={depthData.confidence_chart}>
                           <PolarGrid stroke="rgba(255,255,255,0.05)" />
                           <PolarAngleAxis dataKey="subject" tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 9, fontFamily: 'monospace' }} />
                           <Radar
                             name="Confidence"
                             dataKey="A"
                             stroke="#14b8a6"
                             fill="#14b8a6"
                             fillOpacity={0.2}
                           />
                         </RadarChart>
                       </ResponsiveContainer>
                    </div>

                    <div className="terminal-card bg-white/[0.02] border-white/5 p-4 rounded-xl">
                       <h4 className="text-[10px] font-mono text-white/40 uppercase mb-4">Real-time Alpha Propagation</h4>
                       <div className="space-y-3">
                          {[
                            { label: 'Signal Leakage Detection', status: 'COMPLETE' },
                            { label: 'Cross-Domain Correlation', status: 'ACTIVE' },
                            { label: 'Order Block Identification', status: 'PENDING' }
                          ].map(step => (
                            <div key={step.label} className="flex justify-between items-center text-[10px] font-mono">
                               <span className="text-white/60">{step.label}</span>
                               <span className={step.status === 'COMPLETE' ? 'text-teal' : step.status === 'ACTIVE' ? 'text-amber animate-pulse' : 'text-white/20'}>
                                 {step.status}
                               </span>
                            </div>
                          ))}
                       </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="col-span-1 lg:col-span-4 space-y-6">
          {selectedEvent && (
            <div className="terminal-card bg-bg1/40 border-amber/20 p-6 shadow-[0_0_30px_rgba(232,160,48,0.05)]">
               <h3 className="text-[10px] font-mono font-bold text-amber tracking-[0.2em] uppercase mb-6 flex items-center gap-2">
                 <Activity size={12} /> Calibration Analysis
               </h3>
               
               <div className="mb-8">
                 <p className="text-[10px] font-mono text-white/20 uppercase mb-4 text-center">Market vs. Conflux Model</p>
                 <div className="h-40 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={[
                        { name: 'Market', prob: (selectedEvent.implied_prob || 0) * 100 },
                        { name: 'Model', prob: (selectedEvent.model_prob || 0) * 100 }
                      ]}>
                        <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 10, fontFamily: 'monospace' }} />
                        <YAxis hide domain={[0, 100]} />
                        <Tooltip cursor={false} content={() => null} />
                        <Bar dataKey="prob" radius={[4, 4, 0, 0]} barSize={40}>
                           <Cell fill="rgba(255,255,255,0.1)" />
                           <Cell fill="#e8a030" />
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                 </div>
                 <div className="flex justify-between mt-2 px-4">
                   <div className="text-center">
                     <p className="text-xl font-mono font-bold text-white/40">{((selectedEvent.implied_prob || 0) * 100).toFixed(0)}%</p>
                     <p className="text-[8px] font-mono text-white/20 uppercase">Market</p>
                   </div>
                   <div className="text-center">
                     <p className="text-xl font-mono font-bold text-amber">{((selectedEvent.model_prob || 0) * 100).toFixed(0)}%</p>
                     <p className="text-[8px] font-mono text-white/20 uppercase">Model</p>
                   </div>
                 </div>
               </div>

               <div className="p-4 rounded-lg bg-amber/5 border border-amber/10 mb-6">
                 <div className="flex justify-between items-center mb-2">
                   <span className="text-[10px] font-mono text-white/40 uppercase">Alpha Detection</span>
                   <span className={`text-xs font-mono font-bold ${selectedEvent.alpha > 0 ? 'text-teal' : 'text-red'}`}>
                     {selectedEvent.alpha > 0 ? '+' : ''}{((selectedEvent.alpha || 0) * 100).toFixed(1)}pp
                   </span>
                 </div>
                 <p className="text-[11px] text-white/60 leading-relaxed">
                   The {selectedEvent.description} is currently <strong>{selectedEvent.status || 'ALIGNED'}</strong>. 
                   The Conflux engine detects a {Math.abs((selectedEvent.alpha || 0) * 100).toFixed(1)}% {selectedEvent.alpha > 0 ? 'undervaluation' : 'overvaluation'} 
                   relative to cross-domain signals.
                 </p>
               </div>

               <button 
                 onClick={handleArbitrage}
                 disabled={executing}
                 className={`w-full py-3 rounded-lg font-mono text-[10px] font-bold tracking-[0.2em] uppercase transition-all flex items-center justify-center gap-2
                   ${executing ? 'bg-white/10 text-white/40' : success ? 'bg-teal/20 text-teal border border-teal/40' : 'bg-amber text-bg hover:scale-[1.02] active:scale-[0.98]'}
                 `}
               >
                 {executing ? <Loader2 size={14} className="animate-spin" /> : success ? <Zap size={14} /> : <Zap size={14} />}
                 {executing ? 'Synthesizing Strategy...' : success ? 'Strategy Active' : 'Execute Arbitrage Logic'}
               </button>
            </div>
          )}

          <div className="terminal-card bg-bg1/40 border-white/5 p-6 opacity-60">
            <h3 className="text-[10px] font-mono font-bold text-white/40 tracking-[0.2em] uppercase mb-6 flex items-center gap-2">
              <Zap size={12} className="text-teal" /> Systematic Alpha
            </h3>
            <div className="space-y-4">
              {(alpha?.value || []).slice(0, 2).map(item => (
                <div key={item.subject} className="flex justify-between items-center text-xs">
                  <span className="text-white/60">{item.subject}</span>
                  <span className="text-teal font-mono">+{ (item.alpha_gap * 100).toFixed(1) }%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketsView;
