import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Users, Hash, Zap, TrendingUp, Link2, AreaChart, Sparkles } from 'lucide-react';
import { CardSkeleton, GridSkeleton, DetailSkeleton } from '../components/Skeleton';
import axios from 'axios';
import { AreaChart as ReAreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';

const SocialView = () => {
  const [data, setData] = useState(null);
  const [correlation, setCorrelation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

    const fetchData = async () => {
      try {
        const [socialRes, corrRes] = await Promise.all([
          axios.get('/v1/social/trends', { signal: controller.signal }),
          axios.get('/v1/social/correlation', { signal: controller.signal })
        ]);
        setData(socialRes.data);
        setCorrelation(corrRes.data);
        setLoading(false);
        clearTimeout(timeoutId);
      } catch (err) {
        if (axios.isCancel(err)) return;
        console.error(err);
        setError(err.name === 'AbortError' ? 'Neural Sync Timeout (10s)' : 'Cultural Engine Offline');
        setLoading(false);
      }
    };
    fetchData();
    return () => {
      controller.abort();
      clearTimeout(timeoutId);
    };
  }, []);

  if (loading) return (
    <div className="space-y-8">
      <DetailSkeleton />
    </div>
  );
  if (error) return (
    <div className="p-12 text-center">
      <p className="text-red font-mono text-xs uppercase mb-4">{error}</p>
      <button onClick={() => window.location.reload()} className="px-4 py-2 border border-border rounded-lg text-[10px] font-mono text-muted hover:text-foreground transition-colors">RETRY_LINK</button>
    </div>
  );

  const trends = (data?.topics || []).slice(0, 4).map(t => ({
    tag: `#${t.topic?.replace(/\s+/g, '') || 'unknown'}`,
    volume: '900K+',
    sentiment: t.reddit_signal || 0.5,
    momentum: `+${((t.momentum_score || t.momentum || 0) * 100).toFixed(0)}%`
  }));

  // Synthetic sentiment velocity data
  const velocityData = [
    { time: '00:00', val: 45 }, { time: '04:00', val: 52 }, { time: '08:00', val: 48 },
    { time: '12:00', val: 61 }, { time: '16:00', val: 55 }, { time: '20:00', val: 72 },
    { time: '23:59', val: 68 },
  ];

  return (
    <div className="space-y-8 pb-12">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="col-span-1 lg:col-span-8 space-y-8">
          <div className="terminal-card bg-bg1/20 border-border p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold flex items-center gap-2">
                <Users className="text-coral" size={20} />
                Social & Cultural Trends
              </h3>
              <div className="flex gap-2">
                <span className="px-2 py-0.5 rounded bg-coral/10 border border-coral/20 text-[8px] font-mono text-coral font-bold uppercase">Reddit API: LIVE</span>
                <span className="px-2 py-0.5 rounded bg-amber/10 border border-amber/20 text-[8px] font-mono text-amber font-bold uppercase">Trends: HIGH</span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
              {trends.map(trend => (
                <motion.div 
                  key={trend.tag} 
                  whileHover={{ scale: 1.02 }}
                  className="p-4 rounded-xl border border-border bg-[var(--card-bg)]"
                >
                  <div className="flex justify-between items-start mb-3 gap-4">
                    <span className="text-sm font-bold text-amber truncate break-all">{trend.tag}</span>
                    <span className="text-[10px] font-mono text-teal flex items-center gap-1 shrink-0">
                      <TrendingUp size={10} /> {trend.momentum}
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div>
                      <p className="text-[9px] font-mono text-muted uppercase">Volume</p>
                      <p className="text-lg font-mono font-bold">{trend.volume}</p>
                    </div>
                    <div className="flex-1 h-1 bg-foreground/20 rounded-full overflow-hidden self-end mb-2">
                      <div className="h-full bg-amber" style={{ width: `${trend.sentiment * 100}%` }} />
                    </div>
                    <div className="text-right">
                      <p className="text-[9px] font-mono text-muted uppercase">Sentiment</p>
                      <p className="text-xs font-mono">{(trend.sentiment * 100).toFixed(0)}%</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            <div className="h-48 w-full bg-[var(--card-bg)] rounded-xl border border-border p-4">
               <p className="text-[10px] font-mono text-muted uppercase mb-4 flex items-center gap-2">
                 <AreaChart size={12} /> Sentiment Velocity (24h)
               </p>
               <ResponsiveContainer width="100%" height="100%">
                <ReAreaChart data={velocityData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#e8a030" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#e8a030" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <Tooltip 
                    contentStyle={{ background: '#111', border: '1px solid rgb(var(--foreground-rgb) / 0.1)', fontSize: '10px', fontFamily: 'monospace' }}
                  />
                  <Area type="monotone" dataKey="val" stroke="#e8a030" fillOpacity={1} fill="url(#colorVal)" strokeWidth={2} />
                </ReAreaChart>
               </ResponsiveContainer>
            </div>
          </div>

          <div className="terminal-card bg-bg1/20 border-border p-6">
            <h3 className="text-lg font-bold mb-6 flex items-center gap-2 text-teal">
              <Link2 size={18} />
              Cross-Domain Correlation
            </h3>
            <div className="space-y-4">
              {(correlation?.correlations || []).map(item => (
                <div key={item.topic} className="p-4 rounded-xl border border-border bg-[var(--card-bg)] flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="text-xs font-bold mb-1">{item.topic}</h4>
                    <p className="text-[10px] text-muted italic">{item.description}</p>
                  </div>
                  <div className="flex flex-col sm:flex-row items-end sm:items-center gap-4 sm:gap-8">
                    <div className="text-right sm:text-center">
                       <p className="text-[9px] font-mono text-muted uppercase">Social</p>
                       <p className="text-sm font-mono font-bold text-amber">{(item.social_sentiment * 100).toFixed(0)}%</p>
                    </div>
                    <div className="text-right sm:text-center">
                       <p className="text-[9px] font-mono text-muted uppercase">Market R</p>
                       <p className="text-sm font-mono font-bold text-teal">{item.market_corr.toFixed(2)}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="col-span-1 lg:col-span-4 space-y-6">
          <div className="terminal-card bg-bg1/40 border-amber/20 p-6 shadow-[0_0_30px_rgba(232,160,48,0.05)]">
            <h3 className="text-[10px] font-mono font-bold text-amber tracking-[0.2em] uppercase mb-8 flex items-center gap-2">
              <Sparkles size={12} /> Tipping Point Analysis
            </h3>
            <div className="space-y-8">
              {(data?.topics || []).slice(4, 9).map(t => (
                <div key={t.topic} className="space-y-3">
                  <div className="flex justify-between items-end">
                    <div>
                      <h4 className="text-xs font-bold">{t.topic}</h4>
                      <p className="text-[9px] font-mono text-muted uppercase">{t.category}</p>
                    </div>
                    <span className="text-lg font-mono font-bold text-amber">{((t.tipping_score || t.tipping || 0) * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-1 bg-foreground/20 rounded-full overflow-hidden">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${t.tipping_score * 100}%` }}
                      className="h-full bg-amber shadow-[0_0_10px_rgba(232,160,48,0.4)]"
                    />
                  </div>
                  <p className="text-[10px] text-muted leading-relaxed italic border-l border-amber/20 pl-3">
                    {t.is_tipping ? "Imminent cultural breakthrough detected. Mainstream adoption threshold breached." : "Signal building in global networks. High-conviction niche momentum."}
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

export default SocialView;
