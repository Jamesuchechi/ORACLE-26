import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, Shield, Star, DollarSign, TrendingUp, User, 
  ArrowLeft, Activity, Info, BarChart2 
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer 
} from 'recharts';
import { getFlagUrl } from '../utils/flags';

import axios from 'axios';

const TeamDetail = ({ team, onClose }) => {
  const [squadData, setSquadData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [activeTab, setActiveTab] = useState('squad');

  useEffect(() => {
    const fetchSquad = async () => {
      try {
        const resp = await axios.get(`/v1/team/${team.subject}/squad`);
        setSquadData(resp.data);
      } catch (err) {
        console.error("Failed to fetch squad:", err);
        setError("Squad Intel Link Severed");
      } finally {
        setLoading(false);
      }
    };


    if (team) fetchSquad();
  }, [team]);

  if (!team) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="fixed inset-y-0 right-0 w-[550px] bg-bg/95 backdrop-blur-3xl border-l border-white/10 z-[100] shadow-[0_0_80px_rgba(0,0,0,0.8)] flex flex-col overflow-hidden"
    >
      {/* Scanline Overlay */}
      <div className="absolute inset-0 pointer-events-none z-10 opacity-[0.03] bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%)] bg-[length:100%_4px]" />

      <div className="p-6 border-b border-white/5 flex items-center justify-between bg-bg1/50 backdrop-blur-md z-20">
        <div className="flex items-center gap-4">
          <motion.img 
            layoutId={`flag-${team.subject}`}
            src={getFlagUrl(team.subject)} 
            alt={team.subject} 
            className="w-10 h-7 object-cover rounded-sm border border-white/10 shadow-lg"
          />
          <div>
            <h2 className="text-xl font-bold tracking-tight text-white/90 uppercase">{team.subject}</h2>
            <p className="text-[10px] font-mono text-amber/60 uppercase tracking-[0.3em]">Intelligence Vertical I // Profile</p>
          </div>
        </div>
        <button 
          onClick={onClose}
          className="w-10 h-10 rounded-full hover:bg-white/5 flex items-center justify-center transition-all hover:rotate-90"
        >
          <X size={20} className="text-white/40" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto z-20 custom-scrollbar">
        <AnimatePresence mode="wait">
          {!selectedPlayer ? (
            <motion.div 
              key="squad-explorer"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="p-6 space-y-8"
            >
              <div className="grid grid-cols-2 gap-4">
                <StatBox label="Conflux Score" value={team.conflux_score.toFixed(3)} color="text-amber" icon={<Activity size={14}/>} />
                <StatBox label="Squad Valuation" value={loading ? "..." : (squadData?.total_valuation ? `€${(squadData.total_valuation / 1000000).toFixed(0)}M` : 'N/A')} color="text-teal" icon={<DollarSign size={14}/>} />
              </div>

              {/* Roster Explorer */}
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-[10px] font-mono font-bold text-white/40 tracking-[0.2em] uppercase flex items-center gap-2">
                    <Shield size={12} className="text-amber" /> Tactical Roster Explorer
                  </h3>
                  <div className="text-[9px] font-mono text-white/20 uppercase tracking-widest">
                    {squadData?.squad.length || 0} Assets Detected
                  </div>
                </div>
                
                {loading ? (
                <div className="p-12 text-center font-mono text-white/20 animate-pulse uppercase tracking-widest text-[10px]">
                  Intercepting Squad Communications...
                </div>
              ) : error ? (
                <div className="p-12 text-center text-red font-mono uppercase text-[10px]">
                  {error}
                </div>
              ) : (
                  <div className="space-y-3">
                    {squadData?.squad.map((player, idx) => (
                      <motion.div 
                        key={`${player.name}-${idx}`} 
                        initial={{ opacity: 0, x: 10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        onClick={() => setSelectedPlayer(player)}
                        className="group flex items-center gap-4 p-4 rounded-xl bg-white/[0.02] border border-white/5 hover:border-amber/30 hover:bg-white/[0.04] transition-all cursor-pointer relative overflow-hidden"
                      >
                        <div className="absolute inset-y-0 left-0 w-1 bg-amber scale-y-0 group-hover:scale-y-100 transition-transform origin-top" />
                        <img 
                          src={player.image_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${player.name}`} 
                          alt={player.name} 
                          className="w-12 h-12 rounded-xl bg-bg1 border border-white/10 group-hover:border-amber/50 transition-colors"
                        />
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h4 className="text-sm font-bold text-white/80 group-hover:text-white transition-colors">{player.name}</h4>
                            {player.is_star && <Star size={10} className="fill-amber text-amber" />}
                          </div>
                          <p className="text-[10px] font-mono text-white/30 uppercase tracking-wider">{player.position} • {player.club}</p>
                          <div className="mt-2 w-full flex items-center gap-3">
                            <div className="flex-1 h-1 bg-white/5 rounded-full overflow-hidden">
                              <motion.div 
                                initial={{ width: 0 }}
                                animate={{ width: `${(player.conflux_influence || 0) * 100}%` }}
                                className="h-full bg-amber/40" 
                              />
                            </div>
                            <span className="text-[9px] font-mono text-white/20">{((player.conflux_influence || 0) * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-xs font-mono font-bold text-white/80 tracking-tighter">€{(player.market_value_eur / 1000000).toFixed(1)}M</p>
                          <div className="flex items-center justify-end gap-1 mt-1">
                             <TrendingUp size={10} className="text-teal" />
                             <span className="text-[8px] font-mono text-teal">+1.2%</span>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          ) : (
            <PlayerDetail 
              player={selectedPlayer} 
              team={team}
              onBack={() => setSelectedPlayer(null)} 
            />
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

const PlayerDetail = ({ player, team, onBack }) => {
  // Generate synthetic value history
  const history = [
    { month: 'Oct 25', value: player.market_value_eur * 0.85 },
    { month: 'Nov 25', value: player.market_value_eur * 0.88 },
    { month: 'Dec 25', value: player.market_value_eur * 0.92 },
    { month: 'Jan 26', value: player.market_value_eur * 0.90 },
    { month: 'Feb 26', value: player.market_value_eur * 0.95 },
    { month: 'Mar 26', value: player.market_value_eur },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="p-8 space-y-8"
    >
      <button 
        onClick={onBack}
        className="flex items-center gap-2 text-[10px] font-mono text-white/40 hover:text-white transition-colors uppercase tracking-[0.2em]"
      >
        <ArrowLeft size={14} /> Back to Roster
      </button>

      <div className="flex items-start gap-6">
        <div className="relative">
          <img 
            src={player.image_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${player.name}`} 
            alt={player.name} 
            className="w-32 h-32 rounded-3xl bg-bg1 border border-white/10 shadow-2xl"
          />
          <div className="absolute -bottom-2 -right-2 w-10 h-10 rounded-full bg-bg border border-white/10 flex items-center justify-center overflow-hidden">
            <img src={getFlagUrl(team.subject)} alt={team.subject} className="w-full h-full object-cover" />
          </div>
        </div>
        <div className="flex-1 py-2">
          <h3 className="text-3xl font-bold tracking-tighter mb-1">{player.name}</h3>
          <p className="text-sm font-mono text-amber mb-4 uppercase tracking-widest">{player.position} // {player.club}</p>
          <div className="flex gap-4">
             <div className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/5 flex items-center gap-2">
                <BarChart2 size={12} className="text-teal" />
                <span className="text-[10px] font-mono font-bold">€{(player.market_value_eur / 1000000).toFixed(1)}M</span>
             </div>
             <div className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/5 flex items-center gap-2">
                <Activity size={12} className="text-amber" />
                <span className="text-[10px] font-mono font-bold">{(player.conflux_influence * 100).toFixed(1)}% IMPACT</span>
             </div>
          </div>
        </div>
      </div>

      {/* Valuation History Chart */}
      <div className="terminal-card">
        <h4 className="text-[10px] font-mono font-bold text-white/30 tracking-[0.2em] uppercase mb-6 flex items-center gap-2">
          <TrendingUp size={12} className="text-teal" /> Market Valuation History (€)
        </h4>
        <div className="h-48 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={history}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#14b8a6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
              <XAxis 
                dataKey="month" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fill: '#ffffff20', fontSize: 9, fontFamily: 'monospace' }} 
              />
              <YAxis 
                hide 
                domain={['auto', 'auto']} 
              />
              <Tooltip 
                contentStyle={{ backgroundColor: '#121010', border: '1px solid #ffffff10', borderRadius: '8px' }}
                itemStyle={{ color: '#14b8a6', fontSize: '10px', fontFamily: 'monospace' }}
                labelStyle={{ color: '#ffffff40', fontSize: '10px', fontFamily: 'monospace' }}
                formatter={(value) => [`€${(value / 1000000).toFixed(1)}M`, 'Value']}
              />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="#14b8a6" 
                fillOpacity={1} 
                fill="url(#colorValue)" 
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Intelligence Insights */}
      <div className="grid grid-cols-2 gap-4">
        <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5">
           <h5 className="text-[9px] font-mono text-white/20 uppercase tracking-[0.2em] mb-3 flex items-center gap-2">
             <Info size={12} className="text-amber" /> Tactical Profile
           </h5>
           <ul className="space-y-3">
             <InsightItem label="Work Rate" value="Elite" />
             <InsightItem label="Market Liquidity" value="High" />
             <InsightItem label="Social Momentum" value="Rising" />
           </ul>
        </div>
        <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5">
           <h5 className="text-[9px] font-mono text-white/20 uppercase tracking-[0.2em] mb-3 flex items-center gap-2">
             <Shield size={12} className="text-teal" /> Conflux Matrix
           </h5>
           <ul className="space-y-3">
             <InsightItem label="Econ Resilience" value="Stable" />
             <InsightItem label="Venue Synergy" value="0.84" />
             <InsightItem label="Team Cohesion" value="0.72" />
           </ul>
        </div>
      </div>
    </motion.div>
  );
};

const InsightItem = ({ label, value }) => (
  <li className="flex justify-between items-center">
    <span className="text-[10px] font-mono text-white/40">{label}</span>
    <span className="text-[10px] font-mono font-bold text-white/70">{value}</span>
  </li>
);

const StatBox = ({ label, value, color, icon }) => (
  <div className="p-5 rounded-2xl border border-white/10 bg-white/[0.02] relative overflow-hidden group">
    <div className="absolute top-0 right-0 p-3 text-white/5 group-hover:text-white/10 transition-colors">
      {icon}
    </div>
    <p className="text-[10px] font-mono text-white/20 uppercase mb-2 tracking-widest">{label}</p>
    <p className={`text-2xl font-mono font-bold tracking-tighter ${color}`}>{value}</p>
  </div>
);

export default TeamDetail;

