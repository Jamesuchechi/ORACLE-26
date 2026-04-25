
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

import { Landmark, TrendingUp, ArrowUpRight, ArrowDownRight, Activity, DollarSign } from 'lucide-react';
import axios from 'axios';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, Cell 
} from 'recharts';


const FinanceView = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState(null);

  useEffect(() => {
    axios.get('/v1/finance/dashboard')
      .then(res => {
        setData(res.data);
        if (res.data.highlights?.length > 0) {
          setSelectedTeam(res.data.highlights[0].team);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError(err.code === 'ECONNABORTED' ? 'Connection Timeout' : 'Macro Engine Offline');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-12 text-center font-mono text-white/20 animate-pulse uppercase tracking-widest text-xs">Syncing Macro-Economic Signals...</div>;
  if (error) return (
    <div className="p-12 text-center">
      <p className="text-red font-mono text-xs uppercase mb-4">{error}</p>
      <button onClick={() => window.location.reload()} className="px-4 py-2 border border-white/10 rounded-lg text-[10px] font-mono text-white/40 hover:text-white transition-colors">RETRY_LINK</button>
    </div>
  );

  const highlights = data?.highlights || [];
  const selectedData = highlights.find(h => h.team === selectedTeam);

  const indicators = highlights.slice(0, 4).map(h => ({
    name: `${h.team || 'N/A'} GDP Growth`,
    value: h.gdp_growth !== undefined && h.gdp_growth !== null ? `${h.gdp_growth}%` : 'N/A',
    change: h.gdp_growth > 0 ? '+0.2%' : (h.gdp_growth < 0 ? '-0.1%' : '0.0%'),
    status: (h.econ_signal || 0) > 0.6 ? 'stable' : 'volatile'
  }));

  return (
    <div className="space-y-8 pb-12">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
        {indicators.map(ind => (
          <div key={ind.name} className="terminal-card bg-bg1/20 border-white/5 p-3 lg:p-4">
            <p className="text-[9px] lg:text-[10px] font-mono text-white/20 uppercase mb-1 truncate">{ind.name}</p>
            <div className="flex items-end justify-between gap-2">
              <p className="text-xl lg:text-2xl font-mono font-bold truncate">{ind.value}</p>
              <span className={`text-[10px] font-mono shrink-0 ${ind.change.startsWith('+') ? 'text-teal' : 'text-red'}`}>
                {ind.change}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="col-span-1 lg:col-span-8 space-y-8">
          <div className="terminal-card bg-bg1/20 border-white/5 p-6 h-[400px] flex flex-col">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-[10px] font-mono font-bold text-white/40 tracking-[0.2em] uppercase flex items-center gap-2">
                <Activity size={12} className="text-amber" /> Macro-Economic Signal Matrix
              </h3>
              <div className="flex gap-4">
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 bg-amber rounded-full" />
                  <span className="text-[9px] font-mono text-white/40 uppercase">GDP</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 bg-blue rounded-full" />
                  <span className="text-[9px] font-mono text-white/40 uppercase">Inflation</span>
                </div>
              </div>
            </div>
            
            <div className="flex-1 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart 
                  data={highlights.slice(0, 8)}
                  margin={{ top: 10, right: 10, left: -25, bottom: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis 
                    dataKey="team" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 9, fontFamily: 'monospace' }}
                    interval={0}
                    angle={window.innerWidth < 640 ? -45 : 0}
                    textAnchor={window.innerWidth < 640 ? 'end' : 'middle'}
                    height={40}
                  />
                  <YAxis 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 9, fontFamily: 'monospace' }}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f1114', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                    itemStyle={{ fontSize: '11px', fontFamily: 'monospace' }}
                  />
                  <Bar dataKey="gdp_growth" name="GDP Growth" radius={[2, 2, 0, 0]} barSize={window.innerWidth < 640 ? 10 : 25}>
                    {highlights.slice(0, 8).map((entry, index) => (
                      <Cell key={`cell-gdp-${index}`} fill={entry.team === selectedTeam ? '#e8a030' : 'rgba(232, 160, 48, 0.3)'} />
                    ))}
                  </Bar>
                  <Bar dataKey="inflation" name="Inflation" radius={[2, 2, 0, 0]} barSize={window.innerWidth < 640 ? 10 : 25}>
                    {highlights.slice(0, 8).map((entry, index) => (
                      <Cell key={`cell-inf-${index}`} fill={entry.team === selectedTeam ? '#5b9cf6' : 'rgba(91, 156, 246, 0.3)'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
        <div className="col-span-1 lg:col-span-4 flex flex-col gap-6">
          <div className="terminal-card bg-bg1/40 border-white/5 p-6 flex-1 overflow-y-auto max-h-[400px]">
            <h3 className="text-sm font-bold mb-4 flex items-center gap-2">
              <Landmark size={16} className="text-amber" />
              Equity Signals
            </h3>
            <div className="space-y-3">
              {highlights.map(h => (
                <div 
                  key={h.team} 
                  onClick={() => setSelectedTeam(h.team)}
                  className={`flex justify-between items-center p-3 rounded border cursor-pointer transition-all ${
                    h.team === selectedTeam 
                      ? 'border-amber/50 bg-amber/5 shadow-[0_0_15px_rgba(232,160,48,0.1)]' 
                      : 'border-white/5 bg-white/[0.02] hover:bg-white/[0.05]'
                  }`}
                >
                  <span className={`text-xs font-mono uppercase ${h.team === selectedTeam ? 'text-amber' : 'text-white/70'}`}>{h.team}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-teal">{h.econ_signal.toFixed(2)} SIGNAL</span>
                    <ArrowUpRight size={14} className={`transition-transform ${h.team === selectedTeam ? 'translate-x-0.5 -translate-y-0.5 text-amber' : 'text-teal'}`} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <AnimatePresence mode="wait">
            {selectedData && (
              <motion.div 
                key={selectedTeam}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="terminal-card bg-amber/5 border-amber/20 p-5"
              >
                <div className="flex justify-between items-start mb-4">
                  <h4 className="text-xs font-bold text-amber uppercase tracking-widest">{selectedTeam} Intel</h4>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber/20 text-amber">{selectedData.status}</span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-[9px] font-mono text-white/30 uppercase">GDP Growth</p>
                    <p className="text-lg font-mono font-bold text-white/90">{selectedData.gdp_growth}%</p>
                  </div>
                  <div>
                    <p className="text-[9px] font-mono text-white/30 uppercase">Unemployment</p>
                    <p className="text-lg font-mono font-bold text-white/90">{selectedData.unemployment}%</p>
                  </div>
                  <div className="col-span-2 pt-2 border-t border-white/5">
                    <p className="text-[9px] font-mono text-white/30 uppercase mb-1">Signal Interpretation</p>
                    <p className="text-[11px] leading-relaxed text-white/60">
                      Economic output is currently <span className="text-amber">{(selectedData?.status || 'Stable').toLowerCase()}</span>. 
                      Inflation is holding at <span className="text-blue">{selectedData?.inflation || '0.0'}%</span>, 
                      providing a <span className="text-teal">robust</span> foundation for localized signal acceleration.
                    </p>
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


export default FinanceView;
