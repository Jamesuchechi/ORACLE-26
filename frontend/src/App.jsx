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
  Swords,
  ArrowUpRight,
  ArrowDownRight,
  MessageSquare,
  Landmark,
  Users,
  Menu,
  X,
  Trophy
} from 'lucide-react';

import { useIntelligence } from './hooks/useIntelligence';
import Leaderboard from './components/Leaderboard';
import IntelligenceControls from './components/IntelligenceControls';
import VenueRiskGrid from './components/VenueRiskGrid';
import MatchPredictor from './components/MatchPredictor';
import AnalystChat from './components/AnalystChat';
import SignalRadar from './components/SignalRadar';
import SignalStream from './components/SignalStream';
import { getFlagUrl } from './utils/flags';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

// Main Shell Component
const Shell = ({ children, briefing, currentView, onViewChange }) => (
  <div className="h-screen w-full bg-bg flex flex-col overflow-hidden relative font-sans text-white/80 selection:bg-amber/30 selection:text-amber">
    {/* Cinematic Polish: CRT & Scanlines */}
    <div className="crt-overlay opacity-[0.12]" />
    <div className="scanline-move" />
    
    <header className="h-14 border-b border-white/5 bg-bg1/60 backdrop-blur-xl flex items-center px-4 lg:px-6 justify-between shrink-0 z-50">
      <div className="flex items-center gap-3">
        <button 
          onClick={() => onViewChange('toggleMobileMenu')}
          className="lg:hidden p-2 text-white/60 hover:text-white transition-colors"
        >
          {currentView === 'mobileMenuOpen' ? <X size={20} /> : <Menu size={20} />}
        </button>
        <motion.div 
          animate={{ rotate: [0, 90, 180, 270, 360] }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          className="text-amber text-xl hidden xs:block"
        >
          ◈
        </motion.div>
        <h1 className="font-mono text-[10px] lg:text-xs tracking-[0.2em] lg:tracking-[0.3em] font-bold text-white/90 truncate">
          CONFLUX <span className="text-white/20 font-light ml-1 hidden sm:inline">v.2.0.26 // INTELLIGENCE TERMINAL</span>
        </h1>
      </div>
      
      <div className="flex items-center gap-4 lg:gap-8">
        <div className="flex items-center gap-2 text-[8px] lg:text-[9px] font-mono text-teal tracking-[0.1em] lg:tracking-[0.2em] uppercase bg-teal/5 px-2 lg:px-3 py-1 rounded-full border border-teal/20">
          <div className="w-1.5 h-1.5 rounded-full bg-teal animate-pulse shadow-[0_0_8px_rgba(20,184,166,0.8)]" />
          <span className="hidden xs:inline">Neural Link:</span> Stable
        </div>
        <div className="text-[10px] font-mono text-white/20 tracking-widest uppercase hidden md:flex items-center gap-3">
          <Clock size={12} className="text-white/10" />
          {new Date().toISOString().replace('T', ' ').slice(0, 19)} UTC
        </div>
      </div>
    </header>

    <main className="flex-1 flex overflow-hidden relative">
      {/* Sidebar Drawer */}
      <AnimatePresence>
        {(currentView === 'mobileMenuOpen' || typeof window !== 'undefined' && window.innerWidth > 1024) && (
          <motion.nav 
            initial={{ x: -280 }}
            animate={{ x: 0 }}
            exit={{ x: -280 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className={`fixed lg:relative inset-y-0 left-0 w-64 border-r border-white/5 bg-bg1/90 lg:bg-bg1/40 backdrop-blur-3xl flex flex-col py-8 shrink-0 z-[60] lg:z-40`}
          >
            <div className="px-6 mb-10">
              <p className="text-[9px] font-mono text-white/20 tracking-[0.3em] uppercase mb-6 flex items-center gap-2">
                <Shield size={10} /> Active Verticals
              </p>
              <div className="space-y-1.5">
                <NavItem 
                  icon={<Activity size={14}/>} 
                  label="WC2026 Simulation" 
                  active={currentView === 'dashboard'} 
                  badge="V-I" 
                  onClick={() => onViewChange('dashboard')}
                />
                <NavItem 
                  icon={<Trophy size={14}/>} 
                  label="Bracket Simulator" 
                  active={currentView === 'bracket'} 
                  badge="PRO" 
                  onClick={() => onViewChange('bracket')}
                />
                <NavItem 
                  icon={<Swords size={14}/>} 
                  label="Tactical Matchup" 
                  active={currentView === 'simulator'} 
                  badge="LIVE" 
                  onClick={() => onViewChange('simulator')}
                />
                <NavItem 
                  icon={<TrendingUp size={14}/>} 
                  label="Market Calibration" 
                  active={currentView === 'markets'}
                  badge="V-II" 
                  onClick={() => onViewChange('markets')}
                />
                <NavItem 
                  icon={<Landmark size={14}/>} 
                  label="Finance & Economics" 
                  active={currentView === 'finance'}
                  badge="V-III" 
                  onClick={() => onViewChange('finance')}
                />
                <NavItem 
                  icon={<CloudRain size={14}/>} 
                  label="Climate Risk" 
                  active={currentView === 'climate'}
                  badge="V-IV" 
                  onClick={() => onViewChange('climate')}
                />
                <NavItem 
                  icon={<Users size={14}/>} 
                  label="Social Trends" 
                  active={currentView === 'social'}
                  badge="V-V" 
                  onClick={() => onViewChange('social')}
                />
              </div>
            </div>

            <div className="px-6 mb-10">
              <p className="text-[9px] font-mono text-white/20 tracking-[0.3em] uppercase mb-6 flex items-center gap-2">
                <Cpu size={10} /> Core Modules
              </p>
              <div className="space-y-1.5">
                <NavItem 
                  icon={<Cpu size={14}/>} 
                  label="Fusion Hub" 
                  active={currentView === 'fusion'}
                  badge="CORE" 
                  onClick={() => onViewChange('fusion')}
                />
                <NavItem 
                  icon={<Zap size={14}/>} 
                  label="Alpha Discovery" 
                  active={currentView === 'alpha'}
                  badge="NEW" 
                  onClick={() => onViewChange('alpha')}
                />
              </div>
            </div>
            
            <div className="mt-auto px-6">
              <div className="p-4 rounded-2xl bg-amber/5 border border-amber/10 relative overflow-hidden group">
                 <div className="absolute top-0 left-0 w-1 h-full bg-amber scale-y-0 group-hover:scale-y-100 transition-transform origin-top" />
                 <div className="flex items-center gap-2 mb-3">
                    <div className="w-6 h-6 rounded-lg bg-amber/20 flex items-center justify-center text-amber text-[10px] font-bold">AI</div>
                    <p className="text-[10px] font-bold text-amber/80 uppercase tracking-widest">Analyst Briefing</p>
                 </div>
                 <p className="text-[10px] text-white/40 leading-relaxed line-clamp-3 font-medium">
                   {briefing?.summary || "Analyzing current signal confluence for anomalies..."}
                 </p>
              </div>
            </div>
          </motion.nav>
        )}
      </AnimatePresence>

      {/* Backdrop */}
      <AnimatePresence>
        {currentView === 'mobileMenuOpen' && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => onViewChange('closeMobileMenu')}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[55] lg:hidden"
          />
        )}
      </AnimatePresence>
      
      <section className="flex-1 overflow-y-auto p-4 lg:p-10 relative scroll-smooth bg-[radial-gradient(circle_at_top_right,_rgba(245,158,11,0.03),_transparent_40%)]">
        {children}
      </section>
    </main>

    <footer className="h-10 border-t border-white/5 bg-bg1/90 backdrop-blur-xl flex items-center overflow-hidden shrink-0 z-50">
      <div className="flex gap-16 whitespace-nowrap px-8 animate-[ticker_60s_linear_infinite]">
        <TickerItem label="INDEX ◈ WORLD CUP" value="98.2" />
        <TickerItem label="VOL ◈ MARKETS" value="HIGH" color="text-red" />
        <TickerItem label="ECON ◈ USA GDP" value="+2.4%" color="text-teal" />
        <TickerItem label="CLIMATE ◈ GRID" value="STABLE" color="text-teal" />
        <TickerItem label="SOCIAL ◈ MOMENTUM" value="TIPPING" color="text-amber" />
        <TickerItem label="ALPHA ◈ DETECTION" value="ACTIVE" color="text-teal" />
        {/* Duplicate for seamless loop */}
        <TickerItem label="INDEX ◈ WORLD CUP" value="98.2" />
        <TickerItem label="VOL ◈ MARKETS" value="HIGH" color="text-red" />
        <TickerItem label="ECON ◈ USA GDP" value="+2.4%" color="text-teal" />
      </div>
    </footer>
  </div>
);


const NavItem = ({ icon, label, active, badge, onClick }) => (
  <div 
    onClick={onClick}
    className={`flex items-center gap-3 px-3 py-2 rounded-md cursor-pointer transition-all group ${active ? 'bg-amber/5 text-amber border-l-2 border-amber' : 'text-white/30 hover:text-white/60 hover:bg-white/5'}`}
  >
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

import DashboardView from './views/Dashboard';
import MarketsView from './views/Markets';
import FinanceView from './views/Finance';
import ClimateView from './views/Climate';
import SocialView from './views/Social';
import TeamDetail from './views/TeamDetail';
import FusionView from './views/Fusion';
import AlphaView from './views/Alpha';
import SimulatorView from './views/SimulatorView';

// Main App Component
const App = () => {
  const { rankings, weights, updateWeight, alpha, briefing, venues, predictMatch, loading } = useIntelligence();
  const [view, setView] = useState('dashboard');
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleViewChange = (newView) => {
    if (newView === 'toggleMobileMenu') {
      setIsMobileMenuOpen(!isMobileMenuOpen);
    } else if (newView === 'closeMobileMenu') {
      setIsMobileMenuOpen(false);
    } else {
      setView(newView);
      setIsMobileMenuOpen(false);
    }
  };

  const renderView = () => {
    switch (view) {
      case 'dashboard':
        return (
          <DashboardView 
            rankings={rankings} 
            loading={loading} 
            venues={venues} 
            weights={weights} 
            updateWeight={updateWeight} 
            alpha={alpha} 
            briefing={briefing}
            onTeamClick={setSelectedTeam}
          />
        );
      case 'bracket':
        return (
          <motion.div 
            key="bracket"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
          >
            <SimulatorView />
          </motion.div>
        );
      case 'simulator':
        return (
          <motion.div 
            key="simulator"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="max-w-4xl mx-auto"
          >
            <MatchPredictor rankings={rankings} venues={venues} onPredict={predictMatch} />
          </motion.div>
        );
      case 'markets':
        return <MarketsView alpha={alpha} rankings={rankings} />;
      case 'finance':
        return <FinanceView />;
      case 'climate':
        return <ClimateView venues={venues} />;
      case 'social':
        return <SocialView />;
      case 'fusion':
        return <FusionView />;
      case 'alpha':
        return <AlphaView />;
      default:
        return <DashboardView rankings={rankings} loading={loading} venues={venues} />;
    }
  };

  const getHeaderInfo = () => {
    switch (view) {
      case 'dashboard': return { v: 'I', title: 'World Cup 2026 Simulation', desc: 'Multi-signal fusion engine analyzing the 48-team field across sports performance, prediction markets, macro-economics, and climate resilience.' };
      case 'bracket': return { v: 'I', title: 'Tournament Bracket Simulator', desc: 'Monte Carlo simulation of the full 12-group tournament based on conflux signals.' };
      case 'simulator': return { v: 'I', title: 'Tactical Matchup Predictor', desc: 'Simulate specific matchups by choosing two teams and a venue.' };
      case 'markets': return { v: 'II', title: 'Market Calibration', desc: 'Real-time prediction market signal analysis and alpha detection.' };
      case 'finance': return { v: 'III', title: 'Finance & Economics', desc: 'Macro-economic indicators and financial signals integrated into the conflux engine.' };
      case 'climate': return { v: 'IV', title: 'Climate & Energy', desc: 'Regional climate risk assessment and venue-specific environmental stressors.' };
      case 'social': return { v: 'V', title: 'Social & Cultural Trends', desc: 'Identifying cultural tipping points and social momentum signals.' };
      case 'fusion': return { v: 'CORE', title: 'Fusion Hub', desc: 'Central cross-domain intelligence synchronization matrix.' };
      case 'alpha': return { v: 'SIGMA', title: 'Alpha Discovery', desc: 'Surfacing high-conviction market divergences and strategic arbitrage opportunities.' };
      default: return { v: 'I', title: 'Intelligence Terminal', desc: 'Select a vertical to begin analysis.' };
    }
  };

  const headerInfo = getHeaderInfo();

  return (
    <Shell briefing={briefing} currentView={isMobileMenuOpen ? 'mobileMenuOpen' : view} onViewChange={handleViewChange}>
      <AnalystChat isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
      
      <AnimatePresence>
        {selectedTeam && (
          <TeamDetail team={selectedTeam} onClose={() => setSelectedTeam(null)} />
        )}
      </AnimatePresence>
      
      <button 
        onClick={() => setIsChatOpen(true)}
        className="fixed bottom-12 right-12 w-14 h-14 rounded-full bg-amber text-bg shadow-[0_0_20px_rgba(245,158,11,0.4)] flex items-center justify-center hover:scale-110 active:scale-95 transition-all z-[80]"
      >
        <MessageSquare size={24} />
      </button>

      <div className="max-w-7xl mx-auto pb-12">
        <motion.div 
          key={view}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10 flex flex-col lg:flex-row justify-between items-start lg:items-end gap-6"
        >
          <div>
            <div className="flex items-center gap-2 text-[10px] font-mono text-amber mb-2 uppercase tracking-[0.4em]">
              <Shield size={12} /> Intelligence Vertical {headerInfo.v}
            </div>
            <h2 className="text-2xl lg:text-4xl font-bold mb-3 tracking-tight">
              {headerInfo.title}
            </h2>
            <p className="text-white/40 text-xs lg:text-sm max-w-2xl font-medium leading-relaxed">
              {headerInfo.desc}
            </p>
          </div>
          
          <div className="bg-bg1/40 border border-white/5 p-4 rounded-xl flex items-center gap-4 w-full lg:w-auto">
            <div className="w-10 h-10 rounded-lg bg-amber/5 flex items-center justify-center text-amber">
              <Clock size={20} />
            </div>
            <div>
              <p className="text-[9px] text-white/20 uppercase tracking-[0.2em]">Countdown</p>
              <p className="text-xl font-mono font-bold tracking-tighter">
                {Math.max(0, Math.ceil((new Date('2026-06-11') - new Date()) / 86400000))} 
                <span className="text-xs text-white/10 font-normal ml-1">DAYS</span>
              </p>
            </div>
          </div>
        </motion.div>

        <AnimatePresence mode="wait">
          <motion.div 
            key={view}
            initial={{ opacity: 0, x: 20, filter: 'blur(10px)' }}
            animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
            exit={{ opacity: 0, x: -20, filter: 'blur(10px)' }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            {renderView()}
          </motion.div>
        </AnimatePresence>

      </div>
    </Shell>
  );
};


const AlphaRadar = ({ alpha, rankings }) => {
  const [expandedTeam, setExpandedTeam] = useState(null);

  return (
    <div className="terminal-card bg-bg1/40 border-white/5">
      <h3 className="text-[10px] font-mono font-bold text-white/40 tracking-[0.2em] uppercase mb-4 flex items-center gap-2">
        <Zap size={12} className="text-teal" /> Alpha Radar
      </h3>
      <div className="space-y-3">
        {alpha?.value?.map((item, idx) => (
          <AlphaItem 
            key={`value-${item.subject}-${idx}`} 
            item={item} 
            type="value" 
            fullData={rankings.find(r => r.subject === item.subject)}
            isExpanded={expandedTeam === item.subject}
            onToggle={() => setExpandedTeam(expandedTeam === item.subject ? null : item.subject)}
          />
        ))}
        {alpha?.hype?.map((item, idx) => (
          <AlphaItem 
            key={`hype-${item.subject}-${idx}`} 
            item={item} 
            type="hype" 
            fullData={rankings.find(r => r.subject === item.subject)}
            isExpanded={expandedTeam === item.subject}
            onToggle={() => setExpandedTeam(expandedTeam === item.subject ? null : item.subject)}
          />
        ))}
      </div>
    </div>
  );
};

const AnalystSummary = ({ briefing }) => (
  <div className="terminal-card bg-bg1/40 border-white/5">
    <h3 className="text-[10px] font-mono font-bold text-white/40 tracking-[0.2em] uppercase mb-4 flex items-center gap-2">
      <AlertTriangle size={12} className="text-amber" /> Analyst Summary
    </h3>
    <div className="space-y-4">
      <div className="text-[11px] text-white/60 leading-relaxed prose prose-invert max-w-none">
        <ReactMarkdown>{briefing?.summary}</ReactMarkdown>
      </div>
      <div className="space-y-3">
         {briefing?.key_bullets.map((bullet, i) => (
           <div key={i} className="flex gap-2 text-[10px] text-white/40 font-mono items-start">
             <span className="text-amber shrink-0 mt-0.5">→</span> 
             <div className="prose-xs prose-invert leading-tight">
               <ReactMarkdown>{bullet}</ReactMarkdown>
             </div>
           </div>
         ))}
      </div>
    </div>
  </div>
);

const AlphaItem = ({ item, type, fullData, isExpanded, onToggle }) => (
  <motion.div 
    layout
    initial={{ opacity: 0, x: 20 }}
    animate={{ opacity: 1, x: 0 }}
    className={`p-3 rounded-lg border border-white/5 bg-white/[0.02] cursor-pointer hover:bg-white/[0.05] transition-all overflow-hidden`}
    onClick={onToggle}
  >
    <div className="flex justify-between items-center">
      <div className="flex items-center gap-3">
        <img 
          src={getFlagUrl(item.subject)} 
          alt={item.subject} 
          className="w-5 h-3 object-cover rounded-[1px] border border-white/10"
        />
        <div>
          <p className="text-[11px] font-bold tracking-wide">{item.subject}</p>
          <p className="text-[9px] font-mono text-white/20 uppercase">
            {type === 'value' ? 'Underpriced' : 'Overpriced'} ({(item.alpha_gap * 100).toFixed(1)}pp)
          </p>
        </div>
      </div>
      <div className={type === 'value' ? 'text-teal' : 'text-red'}>
        {type === 'value' ? <ArrowUpRight size={18} /> : <ArrowDownRight size={18} />}
      </div>
    </div>

    <AnimatePresence>
      {isExpanded && fullData && (
        <motion.div 
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="mt-4 pt-4 border-t border-white/5"
        >
          <p className="text-[8px] font-mono text-white/30 uppercase mb-2 tracking-widest text-center">Intelligence Fingerprint</p>
          <SignalRadar data={fullData.signal_breakdown} />
          <div className="mt-2 grid grid-cols-2 gap-2 text-[9px] font-mono text-white/40">
             <div className="flex justify-between"><span>CONFLUX</span> <span className="text-amber">{item.conflux_score.toFixed(2)}</span></div>
             <div className="flex justify-between"><span>MARKET</span> <span className="text-white/20">{item.markets.toFixed(2)}</span></div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  </motion.div>
);

export default App;
