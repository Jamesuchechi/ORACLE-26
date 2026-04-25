
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Activity, Shield, MessageSquare, AlertCircle, Share2, Terminal, Globe } from 'lucide-react';
import axios from 'axios';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from 'recharts';

const FusionView = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeCell, setActiveCell] = useState(null);
  const [isScanning, setIsScanning] = useState(false);

  const fetchFusion = async () => {
    try {
      const res = await axios.get('/v1/fusion/hub');
      setData(res.data);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setError('Fusion Core Synchronization Failed');
      setLoading(false);
    }
  };

  const handleRescan = async () => {
    setIsScanning(true);
    await fetchFusion();
    setTimeout(() => setIsScanning(false), 1500);
  };

  useEffect(() => {
    fetchFusion();
    const interval = setInterval(fetchFusion, 10000); 
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="p-12 text-center font-mono text-white/20 animate-pulse uppercase tracking-widest text-xs">Synchronizing Neural Fusion Hub...</div>;
  if (error) return <div className="p-12 text-center text-red font-mono text-xs uppercase">{error}</div>;

  const domains = ['sports', 'markets', 'climate', 'social'];
  const matrix = data.matrix;

  // Radar data from diagonal of matrix (self-influence/current strength)
  const radarData = domains.map(d => ({
    subject: d.toUpperCase(),
    A: matrix[d][d] * 100,
    full: 100
  }));

  return (
    <div className="space-y-8 pb-12">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Col: Matrix & Radar */}
        <div className="col-span-1 lg:col-span-8 space-y-8">
          <div className="terminal-card bg-bg1/20 border-white/5 p-4 lg:p-8 relative overflow-hidden">
             <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue via-teal to-coral opacity-30" />
             <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
               <h3 className="text-xl lg:text-2xl font-bold flex items-center gap-3">
                 <Globe className="text-blue" size={24} />
                 Interaction Matrix
               </h3>
               <div className="text-left sm:text-right">
                 <p className="text-[10px] font-mono text-white/20 uppercase tracking-[0.2em]">Neural Synchronization</p>
                 <p className="text-xs font-mono text-teal">CALIBRATED_ACTIVE</p>
               </div>
             </div>

             <div className="overflow-x-auto pb-4">
               <div className="grid grid-cols-5 gap-2 font-mono min-w-[500px]">
                 <div className="bg-transparent" />
                 {domains.map(d => (
                   <div key={d} className="text-center p-2 text-[10px] text-white/40 uppercase font-bold">{d}</div>
                 ))}

                 {domains.map(d1 => (
                   <React.Fragment key={d1}>
                     <div className="p-3 text-[10px] text-white/40 uppercase font-bold flex items-center">{d1}</div>
                     {domains.map(d2 => {
                       const val = matrix[d1][d2];
                       const isDiagonal = d1 === d2;
                       return (
                         <motion.div 
                           key={`${d1}-${d2}`}
                           onHoverStart={() => setActiveCell({ d1, d2, val })}
                           onHoverEnd={() => setActiveCell(null)}
                           whileHover={{ scale: 1.05, zIndex: 10 }}
                           className={`p-4 rounded border flex flex-col items-center justify-center transition-all cursor-crosshair ${
                             isDiagonal 
                             ? 'bg-white/5 border-white/20' 
                             : val > 0.7 
                             ? 'bg-blue/10 border-blue/30 shadow-[0_0_15px_rgba(59,130,246,0.1)]' 
                             : 'bg-white/[0.02] border-white/5'
                           }`}
                         >
                           <span className={`text-lg font-bold ${val > 0.7 ? 'text-blue' : 'text-white/60'}`}>
                             {val.toFixed(2)}
                           </span>
                         </motion.div>
                       );
                     })}
                   </React.Fragment>
                 ))}
               </div>
             </div>

             <div className="mt-8 p-4 rounded-lg bg-white/[0.02] border border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <Terminal size={16} className="text-white/20" />
                  <p className="text-[10px] lg:text-xs text-white/40">
                    {activeCell 
                      ? `ANALYSIS: ${activeCell.d1.toUpperCase()} → ${activeCell.d2.toUpperCase()} correlation at ${activeCell.val.toFixed(2)}.`
                      : "Hover over interaction cells for detailed signal mapping."
                    }
                  </p>
                </div>
                <div className="flex gap-2">
                  <div className="w-2 h-2 rounded-full bg-blue animate-pulse" />
                  <div className="w-2 h-2 rounded-full bg-teal animate-pulse" style={{ animationDelay: '0.2s' }} />
                  <div className="w-2 h-2 rounded-full bg-coral animate-pulse" style={{ animationDelay: '0.4s' }} />
                </div>
             </div>
          </div>

          <div className="terminal-card bg-bg1/20 border-white/5 p-6">
            <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
              <Activity size={18} className="text-coral" />
              Intelligence Feed
            </h3>
            <div className="space-y-3">
              {data.alerts.map((alert, i) => (
                <motion.div 
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  key={i} 
                  className="p-4 rounded-lg bg-white/[0.01] border-l-2 border-l-white/10 hover:border-l-blue hover:bg-white/[0.03] transition-all flex items-start gap-4"
                >
                  <span className={`px-2 py-0.5 rounded text-[8px] font-mono font-bold mt-1 ${
                    alert.domain === 'CLIMATE' ? 'bg-blue/20 text-blue' : 
                    alert.domain === 'MARKETS' ? 'bg-teal/20 text-teal' : 
                    alert.domain === 'SOCIAL' ? 'bg-amber/20 text-amber' : 'bg-coral/20 text-coral'
                  }`}>
                    {alert.domain}
                  </span>
                  <p className="text-[11px] lg:text-xs text-white/70 leading-relaxed">{alert.msg}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Col: Balance Radar */}
        <div className="col-span-1 lg:col-span-4 space-y-8">
           <div className="terminal-card bg-bg1/40 border-white/10 p-6 lg:p-8 shadow-[0_0_50px_rgba(0,0,0,0.3)]">
              <div className="text-center mb-8">
                <h3 className="text-sm font-bold uppercase tracking-[0.3em] text-white/60 mb-2">Signal Balance</h3>
                <p className="text-[10px] font-mono text-white/20">REAL-TIME CONFLUX RADAR</p>
              </div>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                    <PolarGrid stroke="rgba(255,255,255,0.05)" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 10, fontFamily: 'monospace' }} />
                    <Radar
                      name="Confidence"
                      dataKey="A"
                      stroke="#3b82f6"
                      fill="#3b82f6"
                      fillOpacity={0.2}
                    />
                    <Tooltip 
                      contentStyle={{ background: '#111', border: '1px solid rgba(255,255,255,0.1)', fontSize: '10px', fontFamily: 'monospace' }}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              <div className="mt-8 grid grid-cols-2 gap-4">
                 {radarData.map(d => (
                   <div key={d.subject} className="p-3 lg:p-4 rounded-xl bg-white/[0.02] border border-white/5 text-center lg:text-left">
                      <p className="text-[9px] font-mono text-white/20 uppercase mb-1">{d.subject}</p>
                      <p className="text-lg lg:text-xl font-mono font-bold text-white/80">{d.A.toFixed(0)}%</p>
                   </div>
                 ))}
              </div>
           </div>

           <div className="terminal-card bg-gradient-to-br from-blue/10 to-teal/10 border-blue/20 p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-lg bg-blue/20 text-blue">
                  <Shield size={20} />
                </div>
                <h4 className="font-bold">Model Confidence</h4>
              </div>
              <p className="text-xs text-white/60 leading-relaxed mb-6 italic">
                "Cross-domain verification has reached 94.2% agreement. The current Alpha Discovery engine is operating at peak efficiency."
              </p>
              <button 
                onClick={handleRescan}
                disabled={isScanning}
                className={`w-full py-3 border rounded-xl text-xs font-bold uppercase tracking-widest transition-all ${
                  isScanning 
                  ? 'bg-blue/40 border-blue text-white cursor-wait animate-pulse' 
                  : 'bg-blue/20 hover:bg-blue/30 border-blue/40 text-blue'
                }`}
              >
                {isScanning ? 'SCANNING_DOMAINS...' : 'REQUEST_RESCAN'}
              </button>
           </div>
        </div>
      </div>
    </div>
  );
};

export default FusionView;
