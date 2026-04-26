
import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Globe, TrendingUp, TrendingDown, Activity, AlertTriangle, Shield, Cpu, RefreshCw } from 'lucide-react';
import axios from 'axios';
import { getFlagUrl } from '../utils/flags';
import toast from 'react-hot-toast';

const ProphecyView = () => {
  const [shifts, setShifts] = useState({
    climate_shift: 0,
    finance_shift: 0,
    social_shift: 0,
    market_shift: 0
  });
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const runSimulation = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams(shifts);
      const res = await axios.get(`/v1/predict/prophecy?${params}`);
      setData(res.data);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setError('Neural Link Failure');
      setLoading(false);
    }
  }, [shifts]);

  useEffect(() => {
    const timeout = setTimeout(runSimulation, 500);
    return () => clearTimeout(timeout);
  }, [shifts, runSimulation]);

  const handleShiftChange = (key, val) => {
    setShifts(prev => ({ ...prev, [key]: parseFloat(val) }));
  };

  const resetShifts = () => {
    setShifts({ climate_shift: 0, finance_shift: 0, social_shift: 0, market_shift: 0 });
    toast.success('Simulation Reset');
  };

  return (
    <div className="space-y-8 pb-20">
      {/* Simulation Controls */}
      <div className="terminal-card bg-bg1/40 border-border p-6">
        <div className="flex justify-between items-center mb-8">
          <h3 className="text-[10px] font-mono font-bold text-muted tracking-[0.2em] uppercase flex items-center gap-2">
            <Globe size={12} className="text-amber" /> Global Propagation Controls
          </h3>
          <button 
            onClick={resetShifts}
            className="px-3 py-1 rounded bg-foreground/20 hover:bg-foreground/25 text-[9px] font-mono text-muted uppercase transition-all flex items-center gap-2"
          >
            <RefreshCw size={10} /> Reset Baseline
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <ProphecySlider 
            label="Climate Stress Offset" 
            val={shifts.climate_shift} 
            onChange={(v) => handleShiftChange('climate_shift', v)} 
            color="bg-red"
          />
          <ProphecySlider 
            label="Economic Volatility" 
            val={shifts.finance_shift} 
            onChange={(v) => handleShiftChange('finance_shift', v)} 
            color="bg-teal"
          />
          <ProphecySlider 
            label="Market Sentiment Shift" 
            val={shifts.market_shift} 
            onChange={(v) => handleShiftChange('market_shift', v)} 
            color="bg-amber"
          />
          <ProphecySlider 
            label="Social Momentum Delta" 
            val={shifts.social_shift} 
            onChange={(v) => handleShiftChange('social_shift', v)} 
            color="bg-coral"
          />
        </div>
      </div>

      {loading && !data ? (
        <div className="p-20 text-center font-mono text-[10px] text-muted animate-pulse uppercase tracking-[0.4em]">
          Calculating Non-Linear Propagation...
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Sensitivity List */}
          <div className="lg:col-span-8">
            <div className="terminal-card bg-bg1/20 border-border overflow-hidden">
              <div className="bg-foreground/20 px-6 py-4 flex justify-between items-center border-b border-border">
                <span className="text-[10px] font-mono font-bold text-muted uppercase tracking-widest">Sensitivity Ranking (Top 20)</span>
                <div className="flex items-center gap-4 text-[9px] font-mono">
                  <div className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-teal" /> Gainer</div>
                  <div className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-red" /> Vulnerable</div>
                </div>
              </div>
              
              <div className="divide-y divide-white/5">
                {data?.teams.map((t, idx) => (
                  <motion.div 
                    key={t.team}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.03 }}
                    className="flex items-center justify-between px-6 py-4 hover:bg-[var(--card-bg)] transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <img src={getFlagUrl(t.team)} className="w-5 h-3.5 object-cover rounded-sm" />
                      <div>
                        <p className="text-xs font-bold">{t.team}</p>
                        <p className="text-[9px] font-mono text-muted uppercase tracking-tighter">
                          Base: {t.base_score.toFixed(3)} → New: {t.new_score.toFixed(3)}
                        </p>
                      </div>
                    </div>
                    
                    <div className={`flex items-center gap-2 font-mono text-xs font-bold ${t.delta > 0 ? 'text-teal' : t.delta < 0 ? 'text-red' : 'text-muted'}`}>
                      {t.delta > 0 ? <TrendingUp size={12} /> : t.delta < 0 ? <TrendingDown size={12} /> : null}
                      {t.delta > 0 ? '+' : ''}{(t.delta * 100).toFixed(2)}pp
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>

          {/* Analysis Panel */}
          <div className="lg:col-span-4 space-y-6">
            <div className="terminal-card bg-amber/5 border-amber/20 p-6">
              <h4 className="text-[10px] font-mono font-bold text-amber uppercase tracking-widest mb-6">Prophecy Summary</h4>
              <div className="space-y-6">
                <div>
                  <p className="text-[9px] font-mono text-muted uppercase mb-2">Most Resilient Subject</p>
                  <div className="flex items-center gap-3 p-3 rounded bg-teal/5 border border-teal/20">
                    <img src={getFlagUrl(data?.summary.top_gainer.team)} className="w-6 h-4 rounded-sm" />
                    <p className="text-xs font-bold">{data?.summary.top_gainer.team}</p>
                    <span className="ml-auto text-[10px] font-mono text-teal">+{ (data?.summary.top_gainer.delta * 100).toFixed(1) }pp</span>
                  </div>
                </div>
                
                <div>
                  <p className="text-[9px] font-mono text-muted uppercase mb-2">Most Vulnerable Subject</p>
                  <div className="flex items-center gap-3 p-3 rounded bg-red/5 border border-red/20">
                    <img src={getFlagUrl(data?.summary.top_loser.team)} className="w-6 h-4 rounded-sm" />
                    <p className="text-xs font-bold">{data?.summary.top_loser.team}</p>
                    <span className="ml-auto text-[10px] font-mono text-red">{ (data?.summary.top_loser.delta * 100).toFixed(1) }pp</span>
                  </div>
                </div>

                <div className="pt-6 border-t border-border">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-[9px] font-mono text-muted uppercase">Global Volatility</span>
                    <span className="text-xs font-bold text-amber">{(data?.summary.volatility * 100).toFixed(2)}%</span>
                  </div>
                  <div className="h-1 bg-foreground/20 rounded-full overflow-hidden">
                    <motion.div 
                      animate={{ width: `${Math.min(100, data?.summary.volatility * 1000)}%` }}
                      className="h-full bg-amber shadow-[0_0_10px_rgba(245,158,11,0.5)]"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="terminal-card bg-bg1/40 border-border p-6">
              <p className="text-[10px] font-mono text-muted leading-relaxed italic">
                "The Prophecy Engine calculates non-linear propagation by injecting global perturbations into the signal vector of all subjects. Sensitivity identifies which systems possess the structural resilience to withstand macro-volatility."
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const ProphecySlider = ({ label, val, onChange, color }) => (
  <div className="space-y-4">
    <div className="flex justify-between items-center">
      <label className="text-[9px] font-mono text-muted uppercase tracking-widest">{label}</label>
      <span className={`text-[10px] font-mono font-bold ${val > 0 ? 'text-teal' : val < 0 ? 'text-red' : 'text-muted'}`}>
        {val > 0 ? '+' : ''}{(val * 100).toFixed(0)}%
      </span>
    </div>
    <input 
      type="range" 
      min="-0.5" 
      max="0.5" 
      step="0.05" 
      value={val} 
      onChange={(e) => onChange(e.target.value)}
      className={`w-full h-1 rounded-lg appearance-none cursor-pointer bg-foreground/30 [.light_&]:bg-black/60 accent-amber`}
    />
    <div className="flex justify-between text-[8px] font-mono text-foreground/10">
      <span>NEGATIVE</span>
      <span>BASELINE</span>
      <span>POSITIVE</span>
    </div>
  </div>
);

export default ProphecyView;
