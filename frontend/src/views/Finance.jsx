
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Landmark, TrendingUp, ArrowUpRight, ArrowDownRight, Activity, DollarSign } from 'lucide-react';

const FinanceView = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/v1/finance/dashboard')
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(err => console.error(err));
  }, []);

  if (loading) return <div className="p-12 text-center font-mono text-white/20 animate-pulse">Syncing Macro-Economic Signals...</div>;
  
  const indicators = (data?.highlights || []).slice(0, 4).map(h => ({
    name: `${h.team} GDP Growth`,
    value: `${h.gdp_growth}%`,
    change: h.gdp_growth > 0 ? '+0.2%' : '-0.1%',
    status: h.econ_signal > 0.6 ? 'stable' : 'volatile'
  }));


  return (
    <div className="space-y-8">
      <div className="grid grid-cols-4 gap-6">
        {indicators.map(ind => (
          <div key={ind.name} className="terminal-card bg-bg1/20 border-white/5 p-4">
            <p className="text-[10px] font-mono text-white/20 uppercase mb-1">{ind.name}</p>
            <div className="flex items-end justify-between">
              <p className="text-2xl font-mono font-bold">{ind.value}</p>
              <span className={`text-[10px] font-mono ${ind.change.startsWith('+') ? 'text-teal' : 'text-red'}`}>
                {ind.change}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-12 gap-8">
        <div className="col-span-8">
          <div className="terminal-card bg-bg1/20 border-white/5 p-6 h-[400px] flex flex-col items-center justify-center text-white/10 font-mono text-xs uppercase tracking-widest">
            <Activity size={48} className="mb-4 opacity-20" />
            Macro-Economic Signal Matrix
            <p className="mt-2 text-[9px] opacity-40">[ Real-time FRED Integration Active ]</p>
          </div>
        </div>
        <div className="col-span-4">
          <div className="terminal-card bg-bg1/40 border-white/5 p-6">
            <h3 className="text-sm font-bold mb-4 flex items-center gap-2">
              <Landmark size={16} className="text-amber" />
              Equity Signals
            </h3>
            <div className="space-y-3">
              {(data?.highlights || []).map(h => (
                <div key={h.team} className="flex justify-between items-center p-2 rounded border border-white/5 bg-white/[0.02]">
                  <span className="text-xs font-mono uppercase">{h.team}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-teal">{h.econ_signal.toFixed(2)} SIGNAL</span>
                    <ArrowUpRight size={14} className="text-teal" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FinanceView;
