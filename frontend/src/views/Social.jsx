
import React, { useState, useEffect } from 'react';
import { MessageSquare, Users, Hash, Zap, TrendingUp } from 'lucide-react';

const SocialView = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/v1/social/trends')
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(err => console.error(err));
  }, []);

  if (loading) return <div className="p-12 text-center font-mono text-white/20 animate-pulse">Analyzing Cultural Momentum...</div>;
  
  const trends = (data?.topics || []).slice(0, 4).map(t => ({
    tag: `#${t.topic.replace(' ', '')}`,
    volume: '900K+',
    sentiment: t.sentiment,
    momentum: `+${(t.momentum * 100).toFixed(0)}%`
  }));


  return (
    <div className="space-y-8">
      <div className="grid grid-cols-12 gap-8">
        <div className="col-span-8">
          <div className="terminal-card bg-bg1/20 border-white/5 p-6">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Users className="text-coral" size={20} />
              Social & Cultural Trends
            </h3>
            <div className="grid grid-cols-2 gap-4">
              {trends.map(trend => (
                <div key={trend.tag} className="p-4 rounded-xl border border-white/5 bg-white/[0.02]">
                  <div className="flex justify-between items-start mb-3">
                    <span className="text-sm font-bold text-amber">{trend.tag}</span>
                    <span className="text-[10px] font-mono text-teal">{trend.momentum}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div>
                      <p className="text-[9px] font-mono text-white/20 uppercase">Volume</p>
                      <p className="text-lg font-mono font-bold">{trend.volume}</p>
                    </div>
                    <div className="flex-1 h-1 bg-white/5 rounded-full overflow-hidden self-end mb-2">
                      <div className="h-full bg-amber" style={{ width: `${trend.sentiment * 100}%` }} />
                    </div>
                    <div className="text-right">
                      <p className="text-[9px] font-mono text-white/20 uppercase">Sentiment</p>
                      <p className="text-xs font-mono">{(trend.sentiment * 100).toFixed(0)}%</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="col-span-4">
          <div className="terminal-card bg-bg1/40 border-white/5 p-6 h-full">
            <h3 className="text-[10px] font-mono font-bold text-white/40 tracking-[0.2em] uppercase mb-6 flex items-center gap-2">
              <Zap size={12} className="text-amber" /> Cultural Tipping Points
            </h3>
            <div className="space-y-6">
              {(data?.topics || []).slice(4, 7).map(t => (
                <TippingPoint 
                  key={t.topic}
                  title={t.topic} 
                  prob={t.momentum} 
                  interpretation={t.tipping_point ? "Imminent cultural breakthrough detected." : "Signal building in global networks."}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const TippingPoint = ({ title, prob, interpretation }) => (
  <div className="space-y-2">
    <div className="flex justify-between text-xs font-bold">
      <span>{title}</span>
      <span className="text-amber font-mono">{(prob * 100).toFixed(0)}%</span>
    </div>
    <div className="h-0.5 bg-white/5 rounded-full overflow-hidden">
      <div className="h-full bg-amber/40" style={{ width: `${prob * 100}%` }} />
    </div>
    <p className="text-[10px] text-white/30 italic">{interpretation}</p>
  </div>
);

export default SocialView;
