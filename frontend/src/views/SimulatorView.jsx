
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Users, Shield, TrendingUp, BarChart3, ChevronRight, Activity } from 'lucide-react';
import axios from 'axios';
import { getFlagUrl } from '../utils/flags';

const SimulatorView = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('groups');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get('/v1/predict/wc2026/tournament');
        setData(res.data);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setError('Tournament Engine Link Severed');
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="p-12 text-center font-mono text-muted animate-pulse uppercase tracking-widest text-xs">Simulating 1,000 Tournament Permutations...</div>;
  if (error) return <div className="p-12 text-center text-red font-mono text-xs uppercase">{error}</div>;

  const groups = Object.entries(data?.groups || {}).sort();

  return (
    <div className="space-y-10 pb-20">
      {/* View Controls */}
      <div className="flex gap-4 border-b border-border pb-4">
        <button 
          onClick={() => setActiveTab('groups')}
          className={`px-4 py-2 rounded-lg text-[10px] font-mono uppercase tracking-widest transition-all ${activeTab === 'groups' ? 'bg-amber/10 text-amber border border-amber/20' : 'text-muted hover:text-muted'}`}
        >
          Group Standings
        </button>
        <button 
          onClick={() => setActiveTab('probabilities')}
          className={`px-4 py-2 rounded-lg text-[10px] font-mono uppercase tracking-widest transition-all ${activeTab === 'probabilities' ? 'bg-amber/10 text-amber border border-amber/20' : 'text-muted hover:text-muted'}`}
        >
          Deep Run Probabilities
        </button>
      </div>

      {activeTab === 'groups' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {groups.map(([name, teams], idx) => (
            <motion.div
              key={name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="terminal-card bg-bg1/20 border-border overflow-hidden"
            >
              <div className="bg-foreground/20 px-4 py-3 flex justify-between items-center border-b border-border">
                <h3 className="font-mono text-[10px] font-bold text-foreground/60 tracking-widest uppercase">Group {name}</h3>
                <Trophy size={12} className="text-foreground/10" />
              </div>
              <div className="p-4 space-y-4">
                {teams.map((t, i) => (
                  <div key={t.team} className="flex items-center gap-3 relative group">
                    <div className="w-4 text-[9px] font-mono text-muted">{i + 1}</div>
                    <img 
                      src={getFlagUrl(t.team)} 
                      alt={t.team} 
                      className="w-5 h-3.5 object-cover rounded-sm grayscale-[0.5] group-hover:grayscale-0 transition-all"
                    />
                    <div className="flex-1">
                      <p className={`text-xs font-medium ${i < 2 ? 'text-foreground/90' : 'text-muted'}`}>{t.team}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-[10px] font-mono font-bold text-amber">{t.expected_points} pts</p>
                    </div>
                    
                    {/* Qualification Indicator */}
                    {i < 2 && (
                      <div className="absolute -left-4 w-1 h-full bg-teal/40 rounded-r shadow-[0_0_10px_rgba(20,184,166,0.3)]" />
                    )}
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-8">
            <div className="terminal-card bg-bg1/20 border-border p-6">
              <h3 className="text-sm font-bold mb-8 flex items-center gap-2">
                <BarChart3 size={16} className="text-amber" />
                Knockout Advancement Matrix
              </h3>
              <div className="space-y-6">
                {data.advancement.slice(0, 15).map((t, idx) => (
                  <div key={t.team} className="space-y-2">
                    <div className="flex justify-between items-end">
                      <div className="flex items-center gap-3">
                        <span className="text-[10px] font-mono text-muted">#{idx+1}</span>
                        <img src={getFlagUrl(t.team)} className="w-5 h-3.5 object-cover rounded-sm" />
                        <span className="text-xs font-bold">{t.team}</span>
                      </div>
                      <span className="text-[10px] font-mono text-amber">Win Prob: {(t.probs.winner * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex h-1.5 gap-0.5 rounded-full overflow-hidden bg-foreground/20">
                      <div className="bg-teal h-full shadow-[0_0_10px_rgba(20,184,166,0.4)]" style={{ width: `${t.probs.r16 * 100}%` }} />
                      <div className="bg-teal/40 h-full" style={{ width: `${(t.probs.qf - t.probs.r16) * 100}%` }} />
                      <div className="bg-amber/60 h-full" style={{ width: `${(t.probs.sf - t.probs.qf) * 100}%` }} />
                    </div>
                    <div className="flex justify-between text-[8px] font-mono text-foreground/10 uppercase tracking-tighter">
                      <span>R32</span>
                      <span>R16</span>
                      <span>QF</span>
                      <span>SF</span>
                      <span>Final</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <div className="lg:col-span-4 space-y-6">
            <div className="terminal-card bg-amber/5 border-amber/20 p-6">
              <h3 className="text-[10px] font-mono font-bold text-amber tracking-widest uppercase mb-6 flex items-center gap-2">
                <Activity size={12} /> Probabilistic Insights
              </h3>
              <div className="space-y-6">
                <div className="p-4 rounded-xl bg-[var(--card-bg)] border border-border">
                  <p className="text-[10px] font-mono text-muted uppercase mb-2">Likely Finalists</p>
                  <div className="flex items-center justify-between text-xs font-bold">
                    <div className="flex items-center gap-2">
                      <img src={getFlagUrl(data.advancement[0].team)} className="w-4 h-3 rounded-sm" />
                      {data.advancement[0].team}
                    </div>
                    <div className="text-muted font-light">VS</div>
                    <div className="flex items-center gap-2">
                      {data.advancement[1].team}
                      <img src={getFlagUrl(data.advancement[1].team)} className="w-4 h-3 rounded-sm" />
                    </div>
                  </div>
                  <div className="mt-4 pt-4 border-t border-border text-[10px] italic text-muted leading-relaxed">
                    "Monte Carlo simulations suggest an {((data.advancement[0].probs.winner + data.advancement[1].probs.winner)*100).toFixed(0)}% probability of the trophy being claimed by these two favorites."
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SimulatorView;
