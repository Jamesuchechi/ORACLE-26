
import React, { useState, useEffect } from 'react';
import { CloudRain, Sun, Wind, AlertTriangle, Thermometer } from 'lucide-react';
import VenueRiskGrid from '../components/VenueRiskGrid';

const ClimateView = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/v1/climate/dashboard')
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(err => console.error(err));
  }, []);

  if (loading) return <div className="p-12 text-center font-mono text-white/20 animate-pulse">Scanning Satellite Climate Data...</div>;

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-12 gap-8">
        <div className="col-span-12">
          <div className="terminal-card bg-bg1/20 border-white/5 p-6">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <CloudRain className="text-blue" size={20} />
              Climate Risk Intelligence
            </h3>
            <p className="text-sm text-white/40 mb-8 max-w-3xl">
              Analyzing long-term weather patterns and environmental stressors for the 2026 World Cup venues. 
              Real-time monitoring of heat domes, humidity indices, and altitude impact on athlete performance.
            </p>
            <VenueRiskGrid venues={data?.venue_risks || []} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {(data?.regional_alerts || []).slice(0, 3).map(alert => (
          <RiskCard 
            key={alert.region}
            icon={alert.risk_type === 'heat_grid' ? <Sun className="text-amber" /> : alert.risk_type === 'wildfire' ? <Wind className="text-teal" /> : <AlertTriangle className="text-red" />} 
            title={alert.region} 
            status={alert.severity} 
            desc={`Regional risk analysis for ${alert.region} shows ${alert.risk_type.replace('_', ' ')} vulnerability.`}
          />
        ))}
      </div>
    </div>
  );
};

const RiskCard = ({ icon, title, status, desc }) => (
  <div className="terminal-card bg-bg1/40 border-white/5 p-5">
    <div className="flex items-center gap-3 mb-4">
      <div className="w-8 h-8 rounded-lg bg-bg1 flex items-center justify-center">
        {icon}
      </div>
      <div>
        <h4 className="text-sm font-bold">{title}</h4>
        <span className={`text-[10px] font-mono uppercase ${status === 'Critical' ? 'text-red' : status === 'Elevated' ? 'text-amber' : 'text-teal'}`}>
          {status}
        </span>
      </div>
    </div>
    <p className="text-[11px] text-white/40 leading-relaxed">
      {desc}
    </p>
  </div>
);

export default ClimateView;
