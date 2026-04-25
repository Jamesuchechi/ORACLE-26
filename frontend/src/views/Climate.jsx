
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CloudRain, Sun, Wind, AlertTriangle, Thermometer, Activity, ShieldAlert, Navigation } from 'lucide-react';
import axios from 'axios';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

const ClimateView = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedVenue, setSelectedVenue] = useState(null);
  const [impactData, setImpactData] = useState(null);
  const [loadingImpact, setLoadingImpact] = useState(false);

  useEffect(() => {
    axios.get('/v1/predict/climate/venues')
      .then(res => {
        setData({ venue_risks: res.data });
        if (res.data.length > 0) handleVenueSelect(res.data[0]);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError(err.code === 'ECONNABORTED' ? 'Satellite Link Timeout' : 'Atmospheric Engine Offline');
        setLoading(false);
      });
  }, []);

  const handleVenueSelect = async (venue) => {
    setSelectedVenue(venue);
    setLoadingImpact(true);
    try {
      const res = await axios.get(`/v1/climate/venue/${venue.venue}/impact?team=Argentina`);
      setImpactData(res.data);
      setLoadingImpact(false);
    } catch (err) {
      console.error(err);
      setLoadingImpact(false);
    }
  };

  if (loading) return <div className="p-12 text-center font-mono text-white/20 animate-pulse uppercase tracking-widest text-xs">Scanning Satellite Climate Data...</div>;
  if (error) return (
    <div className="p-12 text-center">
      <p className="text-red font-mono text-xs uppercase mb-4">{error}</p>
      <button onClick={() => window.location.reload()} className="px-4 py-2 border border-white/10 rounded-lg text-[10px] font-mono text-white/40 hover:text-white transition-colors">RETRY_LINK</button>
    </div>
  );

  const radarData = impactData ? [
    { subject: 'Altitude', A: impactData.biometric_load.altitude, full: 100 },
    { subject: 'Heat', A: impactData.biometric_load.heat, full: 100 },
    { subject: 'Humidity', A: impactData.biometric_load.humidity, full: 100 },
    { subject: 'Oxygen', A: 100 - impactData.biometric_load.oxygen_reduction, full: 100 },
    { subject: 'Risk', A: selectedVenue.risk_score * 100, full: 100 },
  ] : [];

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-12 gap-8">
        <div className="col-span-7 space-y-6">
          <div className="terminal-card bg-bg1/20 border-white/5 p-6">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <CloudRain className="text-blue" size={20} />
              Atmospheric Stress Grid
            </h3>
            
            <div className="grid grid-cols-2 gap-4">
              {(data?.venue_risks || []).slice(0, 10).map(venue => (
                <div 
                  key={venue.venue}
                  onClick={() => handleVenueSelect(venue)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    selectedVenue?.venue === venue.venue 
                    ? 'border-blue/40 bg-blue/5 shadow-[0_0_20px_rgba(59,130,246,0.1)]' 
                    : 'border-white/5 bg-white/[0.02] hover:bg-white/[0.05]'
                  }`}
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h4 className="text-sm font-bold">{venue.city}</h4>
                      <p className="text-[9px] font-mono text-white/20 uppercase">{venue.venue}</p>
                    </div>
                    <div className={`px-2 py-0.5 rounded text-[8px] font-mono font-bold ${
                      venue.status === 'CRITICAL' ? 'bg-red/20 text-red' : venue.status === 'WARNING' ? 'bg-amber/20 text-amber' : 'bg-teal/20 text-teal'
                    }`}>
                      {venue.status}
                    </div>
                  </div>
                  <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${venue.risk_score * 100}%` }}
                      className={`h-full ${venue.risk_score > 0.6 ? 'bg-red' : 'bg-blue'}`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="col-span-5 space-y-6">
          <AnimatePresence mode="wait">
            {selectedVenue && (
              <motion.div 
                key={selectedVenue.venue}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="terminal-card bg-bg1/40 border-blue/20 p-6 shadow-[0_0_30px_rgba(59,130,246,0.05)]"
              >
                <div className="flex justify-between items-start mb-8">
                  <div>
                    <h3 className="text-lg font-bold flex items-center gap-2">
                      <Navigation size={18} className="text-blue" />
                      {selectedVenue.city}
                    </h3>
                    <p className="text-[10px] font-mono text-white/40 uppercase">Performance Impact Simulation</p>
                  </div>
                  <div className="text-right">
                    <p className="text-[10px] font-mono text-white/20 uppercase">Penalty Index</p>
                    <p className={`text-2xl font-mono font-bold ${impactData?.performance_penalty > 10 ? 'text-red' : 'text-teal'}`}>
                      -{impactData?.performance_penalty || 0}%
                    </p>
                  </div>
                </div>

                <div className="h-64 w-full mb-8">
                   <p className="text-[10px] font-mono text-white/20 uppercase mb-4 text-center">Biometric Load Breakdown</p>
                   <ResponsiveContainer width="100%" height="100%">
                     <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                       <PolarGrid stroke="rgba(255,255,255,0.05)" />
                       <PolarAngleAxis dataKey="subject" tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 9, fontFamily: 'monospace' }} />
                       <Radar
                         name="Load"
                         dataKey="A"
                         stroke="#3b82f6"
                         fill="#3b82f6"
                         fillOpacity={0.2}
                       />
                     </RadarChart>
                   </ResponsiveContainer>
                </div>

                <div className="p-4 rounded-lg bg-blue/5 border border-blue/10 mb-6">
                  <div className="flex items-center gap-3 mb-3 text-blue">
                    <ShieldAlert size={16} />
                    <span className="text-[10px] font-mono font-bold uppercase tracking-widest">Medical Intelligence</span>
                  </div>
                  <p className="text-xs text-white/70 leading-relaxed italic">
                    "{impactData?.recommendation || "Analyzing optimal metabolic window..."}"
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                   <div className="p-3 rounded-lg bg-white/[0.02] border border-white/5">
                      <p className="text-[9px] font-mono text-white/20 uppercase mb-1">Oxygen Saturation</p>
                      <p className="text-lg font-mono font-bold text-red">-{impactData?.biometric_load.oxygen_reduction}%</p>
                   </div>
                   <div className="p-3 rounded-lg bg-white/[0.02] border border-white/5">
                      <p className="text-[9px] font-mono text-white/20 uppercase mb-1">Heat Stress</p>
                      <p className="text-lg font-mono font-bold text-amber">{impactData?.biometric_load.heat}%</p>
                   </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default ClimateView;
