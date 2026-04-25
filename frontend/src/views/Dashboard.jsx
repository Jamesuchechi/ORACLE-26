
import React from 'react';
import { motion } from 'framer-motion';
import Leaderboard from '../components/Leaderboard';
import VenueRiskGrid from '../components/VenueRiskGrid';
import SignalStream from '../components/SignalStream';
import IntelligenceControls from '../components/IntelligenceControls';
import AnalystSummary from '../components/AnalystSummary'; // I'll extract this too

const DashboardView = ({ rankings, loading, venues, weights, updateWeight, alpha, briefing, onTeamClick }) => {
  return (
    <motion.div 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="grid grid-cols-1 lg:grid-cols-12 gap-8"
    >
      <div className="col-span-1 lg:col-span-8 space-y-8">
        <div className="terminal-card min-h-0 lg:min-h-[500px] border-white/5 bg-bg1/20 backdrop-blur-sm">
          <Leaderboard rankings={rankings} loading={loading} onTeamClick={onTeamClick} />
        </div>
        <VenueRiskGrid venues={venues} />
        {/* On mobile, we want the live signal stream to follow the core data immediately */}
        <div className="lg:hidden">
          <SignalStream />
        </div>
      </div>
      
      <div className="col-span-1 lg:col-span-4 space-y-6">
        <IntelligenceControls weights={weights} onWeightChange={updateWeight} />
        <AlphaRadarBrief alpha={alpha} rankings={rankings} />
        <AnalystSummary briefing={briefing} />
        
        {/* On desktop, the stream sits nicely at the bottom of the main col, but we can also place it here for secondary feed */}
        <div className="hidden lg:block">
          <SignalStream />
        </div>
      </div>
    </motion.div>
  );
};

// Simple inline version of Alpha Radar to avoid missing component
const AlphaRadarBrief = ({ alpha }) => (
  <div className="terminal-card bg-bg1/40 border-white/5 p-4">
    <h3 className="text-[10px] font-mono font-bold text-white/40 tracking-[0.2em] uppercase mb-4 flex items-center gap-2">
      Alpha Radar
    </h3>
    <div className="space-y-2">
      {alpha?.value?.slice(0, 3).map(item => (
        <div key={item.subject} className="flex justify-between items-center text-xs">
          <span>{item.subject}</span>
          <span className="text-teal font-mono">+{ (item.alpha_gap * 100).toFixed(1) }%</span>
        </div>
      ))}
      {!alpha?.value && <div className="text-[10px] text-white/20 italic">Scanning opportunities...</div>}
    </div>
  </div>
);

export default DashboardView;
