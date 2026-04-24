
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Zap, ArrowUpRight, ArrowDownRight, Activity, Globe } from 'lucide-react';
import SignalRadar from '../components/SignalRadar';

const MarketsView = ({ alpha, rankings }) => {
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [marketsData, setMarketsData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/v1/markets/dashboard')
      .then(res => res.json())
      .then(data => {
        setMarketsData(data?.events || []);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-12 text-center font-mono text-white/20 animate-pulse">Synchronizing Market Signals...</div>;


  return (
    <div className="space-y-8">
      <div className="grid grid-cols-12 gap-8">
        <div className="col-span-8 space-y-6">
          <div className="terminal-card bg-bg1/20 border-white/5 p-6">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <TrendingUp className="text-amber" size={20} />
              Prediction Market Calibration
            </h3>
            
            <div className="space-y-4">
              {marketsData.map(market => (
                <div key={market.event_id} className="p-4 rounded-xl border border-white/5 bg-white/[0.02] flex items-center justify-between hover:bg-white/[0.05] transition-all cursor-pointer">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-bg1 flex items-center justify-center text-white/40">
                      <Globe size={18} />
                    </div>
                    <div>
                      <p className="text-[10px] font-mono text-white/20 uppercase tracking-widest">{market.type}</p>
                      <h4 className="text-sm font-bold">{market.description}</h4>
                    </div>
                  </div>
                  <div className="flex items-center gap-8">
                    <div className="text-right">
                      <p className="text-[10px] font-mono text-white/20 uppercase">Implied Prob</p>
                      <p className="text-xl font-mono font-bold text-amber">{(market.implied_prob * 100).toFixed(0)}%</p>
                    </div>
                    <div className="text-teal">
                      <ArrowUpRight size={20} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="col-span-4 space-y-6">
          <div className="terminal-card bg-bg1/40 border-white/5 p-6">
            <h3 className="text-[10px] font-mono font-bold text-white/40 tracking-[0.2em] uppercase mb-6 flex items-center gap-2">
              <Zap size={12} className="text-teal" /> Systematic Alpha
            </h3>
            <div className="space-y-4">
              {(alpha?.value || []).map(item => (
                <div key={item.subject} className="p-4 rounded-lg border border-white/5 bg-teal/5">
                  <div className="flex justify-between mb-2">
                    <span className="text-xs font-bold">{item.subject}</span>
                    <span className="text-[10px] font-mono text-teal">+{ (item.alpha_gap * 100).toFixed(1) }% Alpha</span>
                  </div>
                  <p className="text-[10px] text-white/50 leading-relaxed italic">
                    Conflux model predicts higher probability than current market odds. Potential value detected.
                  </p>
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
