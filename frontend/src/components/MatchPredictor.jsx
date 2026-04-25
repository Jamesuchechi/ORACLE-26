import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Swords, Shield, Zap, TrendingUp, CloudRain, MapPin, Activity } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { getFlagUrl } from '../utils/flags';

const MatchPredictor = ({ rankings, venues, onPredict }) => {
  const [team1, setTeam1] = useState('');
  const [team2, setTeam2] = useState('');
  const [venue, setVenue] = useState('MetLife Stadium');
  const [prediction, setPrediction] = useState(null);
  const [simulating, setSimulating] = useState(false);

  const handleSimulate = async () => {
    if (!team1 || !team2 || team1 === team2) return;
    setSimulating(true);
    setPrediction(null);
    
    // Artificial delay for "Reasoning" feel
    setTimeout(async () => {
      const res = await onPredict(team1, team2, venue);
      setPrediction(res);
      setSimulating(false);
    }, 1200);
  };

  const getTeam = (name) => rankings.find(r => r.subject === name);

  return (
    <div className="terminal-card bg-bg1/40 border-white/5 space-y-8">
      <div className="flex justify-between items-center">
        <h3 className="text-[10px] font-mono font-bold text-white/40 tracking-[0.2em] uppercase flex items-center gap-2">
          <Swords size={12} className="text-amber" /> Conflux Match Simulator
        </h3>
        <div className="flex items-center gap-2 text-[9px] font-mono text-white/20">
          <MapPin size={10} />
          <select 
            value={venue}
            onChange={(e) => setVenue(e.target.value)}
            className="bg-transparent border-none focus:ring-0 text-white/50 cursor-pointer max-w-[140px] sm:max-w-[250px] truncate"
          >
            {venues.map(v => <option key={v.venue} value={v.venue} className="bg-bg1">{v.city} ({v.venue})</option>)}
          </select>
        </div>
      </div>

      <div className="flex flex-col lg:grid lg:grid-cols-11 gap-6 lg:gap-4 items-center">
        {/* Team 1 Selection */}
        <div className="w-full lg:col-span-5 space-y-4">
          <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5 text-center flex flex-col items-center">
            {team1 && (
              <img 
                src={getFlagUrl(team1)} 
                alt={team1} 
                className="w-12 h-8 mb-4 rounded shadow-lg border border-white/10"
              />
            )}
            <select 
              value={team1} 
              onChange={(e) => setTeam1(e.target.value)}
              className="w-full bg-transparent border-none text-xl font-bold text-center focus:ring-0 appearance-none truncate"
            >
              <option value="" className="bg-bg1 text-white/20">Select Team A</option>
              {rankings.map(r => <option key={r.subject} value={r.subject} className="bg-bg1">{r.subject}</option>)}
            </select>
            <p className="text-[10px] font-mono text-white/20 uppercase mt-2">Home / Seed 1</p>
          </div>
          
          {getTeam(team1) && <SignalStats team={getTeam(team1)} />}
        </div>

        {/* VS Divider */}
        <div className="hidden lg:flex lg:col-span-1 flex-col items-center">
           <div className="h-12 w-[1px] bg-white/5 mb-4" />
           <div className="w-8 h-8 rounded-full border border-white/10 flex items-center justify-center text-[10px] font-mono text-white/20">VS</div>
           <div className="h-12 w-[1px] bg-white/5 mt-4" />
        </div>

        <div className="lg:hidden flex items-center justify-center py-2">
          <div className="h-[1px] flex-1 bg-white/5" />
          <div className="px-4 text-[10px] font-mono text-white/10">VERSUS</div>
          <div className="h-[1px] flex-1 bg-white/5" />
        </div>

        {/* Team 2 Selection */}
        <div className="w-full lg:col-span-5 space-y-4">
          <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5 text-center flex flex-col items-center">
            {team2 && (
              <img 
                src={getFlagUrl(team2)} 
                alt={team2} 
                className="w-12 h-8 mb-4 rounded shadow-lg border border-white/10"
              />
            )}
            <select 
              value={team2} 
              onChange={(e) => setTeam2(e.target.value)}
              className="w-full bg-transparent border-none text-xl font-bold text-center focus:ring-0 appearance-none truncate"
            >
              <option value="" className="bg-bg1 text-white/20">Select Team B</option>
              {rankings.map(r => <option key={r.subject} value={r.subject} className="bg-bg1">{r.subject}</option>)}
            </select>
            <p className="text-[10px] font-mono text-white/20 uppercase mt-2">Away / Seed 2</p>
          </div>
          {getTeam(team2) && <SignalStats team={getTeam(team2)} reverse />}
        </div>
      </div>

      <div className="flex justify-center">
        <button 
          onClick={handleSimulate}
          disabled={!team1 || !team2 || simulating}
          className={`px-8 py-3 rounded-lg font-mono text-xs font-bold tracking-[0.2em] uppercase transition-all flex items-center gap-3
            ${!team1 || !team2 ? 'bg-white/5 text-white/20 cursor-not-allowed' : 'bg-amber text-bg hover:scale-105 active:scale-95'}
          `}
        >
          {simulating ? <div className="w-4 h-4 border-2 border-bg/20 border-t-bg rounded-full animate-spin" /> : <Zap size={14} />}
          {simulating ? 'Processing...' : 'Run Simulation'}
        </button>
      </div>

      {/* Prediction Result Overlay */}
      <AnimatePresence>
        {prediction && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="pt-8 border-t border-white/5"
          >
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 lg:gap-6">
              <ProbCard label="WIN" team={team1} prob={prediction.win_prob} color="text-teal" />
              <ProbCard label="DRAW" team="NEUTRAL" prob={prediction.draw_prob} color="text-white/40" />
              <ProbCard label="WIN" team={team2} prob={prediction.loss_prob} color="text-blue" />
            </div>
            
            <div className="mt-8 grid grid-cols-1 gap-4">
               <div className="p-4 rounded-lg bg-bg2/50 border border-white/5">
                  <div className="flex items-center gap-2 mb-3">
                     <Activity size={14} className="text-amber" />
                     <h4 className="text-[10px] font-mono font-bold text-white/40 uppercase tracking-widest">AI Tactical Analysis</h4>
                  </div>
                  <div className="text-[11px] text-white/60 leading-relaxed italic prose-xs prose-invert">
                    <ReactMarkdown>{prediction.intelligence_report}</ReactMarkdown>
                  </div>
               </div>

               <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {Object.entries(prediction.advantages).map(([key, team]) => (
                    <div key={key} className="p-3 rounded-lg border border-white/5 bg-white/[0.01]">
                       <p className="text-[8px] font-mono text-white/20 uppercase mb-1">{key.replace('_', ' ')}</p>
                       <p className="text-[10px] font-bold text-teal flex items-center gap-2 truncate">
                         <Shield size={10} className="shrink-0" /> {team}
                       </p>
                    </div>
                  ))}
               </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

const SignalStats = ({ team, reverse }) => (
  <div className={`space-y-2 ${reverse ? 'text-right' : 'text-left'}`}>
    <div className={`flex items-center gap-2 text-[9px] font-mono text-white/30 ${reverse ? 'flex-row-reverse' : ''}`}>
       <TrendingUp size={10} />
       <span>Sports: {((team?.signal_breakdown?.sports || 0) * 100).toFixed(0)}%</span>
    </div>
    <div className={`flex items-center gap-2 text-[9px] font-mono text-white/30 ${reverse ? 'flex-row-reverse' : ''}`}>
       <CloudRain size={10} />
       <span>Climate: {((team?.signal_breakdown?.climate || 0) * 100).toFixed(0)}%</span>
    </div>
  </div>
);

const ProbCard = ({ label, team, prob, color }) => (
  <div className="text-center p-4 rounded-xl bg-white/[0.01] border border-white/5">
    {team !== 'NEUTRAL' && (
      <img 
        src={getFlagUrl(team)} 
        alt={team} 
        className="w-8 h-5 mx-auto mb-3 rounded-sm shadow-sm border border-white/10"
      />
    )}
    <p className="text-[9px] font-mono text-white/20 uppercase tracking-widest mb-1">{team}</p>
    <p className={`text-2xl lg:text-3xl font-mono font-bold ${color}`}>{(prob * 100).toFixed(1)}%</p>
    <p className="text-[9px] font-bold text-white/10 uppercase mt-1">{label}</p>
  </div>
);

export default MatchPredictor;
