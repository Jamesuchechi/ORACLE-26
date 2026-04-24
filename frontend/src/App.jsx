import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield,
  TrendingUp, 
  CloudRain, 
  Globe, 
  Activity,
  Cpu,
  Clock,
  Zap,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';

import { useIntelligence } from './hooks/useIntelligence';
import Leaderboard from './components/Leaderboard';
import IntelligenceControls from './components/IntelligenceControls';

// Main Shell Component
const Shell = ({ children, briefing }) => (
  <div className="h-screen w-full bg-bg flex flex-col overflow-hidden relative font-sans text-white/80">
    <div className="absolute inset-0 pointer-events-none z-50 opacity-[0.03] bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_4px,3px_100%]" />
    
    <header className="h-14 border-b border-white/5 bg-bg1/50 backdrop-blur-md flex items-center px-6 justify-between shrink-0 z-20">
      <div className="flex items-center gap-3">
        <span className="text-amber text-xl">◈</span>
        <h1 className="font-mono text-sm tracking-[0.2em] font-medium">
          CONFLUX <span className="text-white/30 font-light">INTELLIGENCE TERMINAL</span>
        </h1>
      </div>
      
      <div className="flex items-center gap-8">
        <div className="flex items-center gap-2 text-[10px] font-mono text-teal tracking-widest uppercase">
          <div className="w-1.5 h-1.5 rounded-full bg-teal animate-pulse" />
          Live Signals Active
        </div>
        <div className="text-[10px] font-mono text-white/30 tracking-widest uppercase">
          {new Date().toISOString().replace('T', ' ').slice(0, 19)} UTC
        </div>
      </div>
    </header>

    <main className="flex-1 flex overflow-hidden">
      <nav className="w-56 border-r border-white/5 bg-bg1/30 flex flex-col py-6 shrink-0 z-10">
        <div className="px-4 mb-8">
          <p className="text-[9px] font-mono text-white/20 tracking-[0.2em] uppercase mb-4">Verticals</p>
          <div className="space-y-1">
            <NavItem icon={<Activity size={14}/>} label="WC2026 Prediction" active badge="V-I" />
            <NavItem icon={<TrendingUp size={14}/>} label="Market Calibration" badge="V-II" />
            <NavItem icon={<CloudRain size={14}/>} label="Climate Risk" badge="V-III" />
            <NavItem icon={<Globe size={14}/>} label="Cultural Moments" badge="V-IV" />
          </div>
        </div>

        <div className="px-4 mb-8">
          <p className="text-[9px] font-mono text-white/20 tracking-[0.2em] uppercase mb-4">System</p>
          <div className="space-y-1">
            <NavItem icon={<Cpu size={14}/>} label="Fusion Engine" />
            <NavItem icon={<Zap size={14}/>} label="Alpha Radar" />
          </div>
        </div>
        
        <div className="mt-auto px-4">
          <div className="terminal-card bg-amber/5 border-amber/10 p-3">
             <div className="flex items-center gap-2 mb-2">
                <div className="w-5 h-5 rounded bg-amber/20 flex items-center justify-center text-amber text-[10px] font-bold">Z</div>
                <p className="text-[10px] font-bold text-amber/80 uppercase tracking-wider">Analyst Insight</p>
             </div>
             <p className="text-[10px] text-white/50 leading-relaxed italic">
               {briefing?.headline || "Initializing neural analysis..."}
             </p>
          </div>
        </div>
      </nav>

      <section className="flex-1 overflow-y-auto p-8 relative scroll-smooth">
        {children}
      </section>
    </main>

    <footer className="h-8 border-t border-white/5 bg-bg1/80 backdrop-blur-md flex items-center overflow-hidden shrink-0 z-20">
      <div className="flex gap-12 whitespace-nowrap px-6 animate-[ticker_60s_linear_infinite]">
        <TickerItem label="CONFLUX ◈ ARG" value="21.4%" />
        <TickerItem label="CONFLUX ◈ FRA" value="17.8%" />
        <TickerItem label="POLY: US RECESSION" value="34%" color="text-red" />
        <TickerItem label="CLIMATE: TEXAS HEAT" value="CRITICAL" color="text-red" />
        <TickerItem label="TREND: AI AGENTS" value="TIPPING" color="text-teal" />
        <TickerItem label="ALPHA: MOROCCO" value="+3.1pp" color="text-teal" />
        {/* Duplicate for seamless loop */}
        <TickerItem label="CONFLUX ◈ ARG" value="21.4%" />
        <TickerItem label="CONFLUX ◈ FRA" value="17.8%" />
        <TickerItem label="POLY: US RECESSION" value="34%" color="text-red" />
      </div>
    </footer>
  </div>
);

const NavItem = ({ icon, label, active, badge }) => (
  <div className={`flex items-center gap-3 px-3 py-2 rounded-md cursor-pointer transition-all group ${active ? 'bg-amber/5 text-amber border-l-2 border-amber' : 'text-white/30 hover:text-white/60 hover:bg-white/5'}`}>
    <span className={`${active ? 'text-amber' : 'text-white/10 group-hover:text-white/30'}`}>{icon}</span>
    <span className="text-[11px] font-medium tracking-wide">{label}</span>
    {badge && <span className="ml-auto text-[8px] font-mono bg-white/5 px-1.5 py-0.5 rounded text-white/20">{badge}</span>}
  </div>
);

const TickerItem = ({ label, value, color = "text-amber" }) => (
  <div className="flex items-center gap-2 text-[10px] font-mono uppercase">
    <span className="text-white/20 tracking-widest">{label}</span>
    <span className={`${color} font-bold`}>{value}</span>
  </div>
);

// Main App Component
const App = () => {
  const { rankings, weights, updateWeight, alpha, briefing, loading } = useIntelligence();

  return (
    <Shell briefing={briefing}>
      <div className="max-w-7xl mx-auto pb-12">
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10 flex justify-between items-end"
        >
          <div>
            <div className="flex items-center gap-2 text-[10px] font-mono text-amber mb-2 uppercase tracking-[0.4em]">
              <Shield size={12} /> Intelligence Vertical I
            </div>
            <h2 className="text-4xl font-bold mb-3 tracking-tight">World Cup 2026 <span className="text-white/10">Simulation</span></h2>
            <p className="text-white/40 text-sm max-w-2xl font-medium leading-relaxed">
              Multi-signal fusion engine analyzing the 48-team field across sports performance, prediction markets, macro-economics, and climate resilience.
            </p>
          </div>
          
          <div className="bg-bg1/40 border border-white/5 p-4 rounded-xl flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-amber/5 flex items-center justify-center text-amber">
              <Clock size={20} />
            </div>
            <div>
              <p className="text-[9px] text-white/20 uppercase tracking-[0.2em]">Countdown</p>
              <p className="text-xl font-mono font-bold tracking-tighter">782 <span className="text-xs text-white/10 font-normal">DAYS</span></p>
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-12 gap-8">
          {/* Main Content: Leaderboard */}
          <div className="col-span-8">
            <div className="terminal-card min-h-[600px] border-white/5 bg-bg1/20 backdrop-blur-sm">
               <Leaderboard rankings={rankings} loading={loading} />
            </div>
          </div>
          
          {/* Sidebar: Controls & Alpha */}
          <div className="col-span-4 space-y-6">
            <IntelligenceControls weights={weights} onWeightChange={updateWeight} />
            
            {/* Alpha Radar */}
            <div className="terminal-card bg-bg1/40 border-white/5">
              <h3 className="text-[10px] font-mono font-bold text-white/40 tracking-[0.2em] uppercase mb-4 flex items-center gap-2">
                <Zap size={12} className="text-teal" /> Alpha Radar
              </h3>
              <div className="space-y-3">
                <AnimatePresence>
                  {alpha?.value.map((item) => (
                    <AlphaItem key={item.subject} item={item} type="value" />
                  ))}
                  {alpha?.hype.map((item) => (
                    <AlphaItem key={item.subject} item={item} type="hype" />
                  ))}
                </AnimatePresence>
              </div>
            </div>

            {/* Briefing Card */}
            <div className="terminal-card bg-bg1/40 border-white/5">
              <h3 className="text-[10px] font-mono font-bold text-white/40 tracking-[0.2em] uppercase mb-4 flex items-center gap-2">
                <AlertTriangle size={12} className="text-amber" /> Analyst Summary
              </h3>
              <div className="space-y-4">
                <p className="text-[11px] text-white/60 leading-relaxed">
                  {briefing?.summary}
                </p>
                <div className="space-y-2">
                   {briefing?.key_bullets.map((bullet, i) => (
                     <div key={i} className="flex gap-2 text-[10px] text-white/40 font-mono">
                       <span className="text-amber">→</span> {bullet}
                     </div>
                   ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Shell>
  );
};

const AlphaItem = ({ item, type }) => (
  <motion.div 
    initial={{ opacity: 0, x: 20 }}
    animate={{ opacity: 1, x: 0 }}
    className={`p-3 rounded-lg border border-white/5 flex justify-between items-center bg-white/[0.02]`}
  >
    <div>
      <p className="text-[11px] font-bold tracking-wide">{item.subject}</p>
      <p className="text-[9px] font-mono text-white/20 uppercase">
        {type === 'value' ? 'Underpriced' : 'Overpriced'} ({(item.alpha_gap * 100).toFixed(1)}pp)
      </p>
    </div>
    <div className={type === 'value' ? 'text-teal' : 'text-red'}>
      {type === 'value' ? <ArrowUpRight size={18} /> : <ArrowDownRight size={18} />}
    </div>
  </motion.div>
);

export default App;
