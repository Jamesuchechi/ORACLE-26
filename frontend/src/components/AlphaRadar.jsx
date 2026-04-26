
import React from 'react';
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, Radar, Tooltip } from 'recharts';

const AlphaRadar = ({ alpha, rankings }) => {
  if (!alpha || !alpha.value) return null;

  // Process data for the radar: take top 6 alpha opportunities
  const radarData = alpha.value.slice(0, 6).map(item => ({
    subject: item.subject || item.description,
    alpha: item.alpha_gap * 100,
    fullMark: 15
  }));

  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
          <PolarGrid stroke="rgb(var(--foreground-rgb) / 0.05)" />
          <PolarAngleAxis 
            dataKey="subject" 
            tick={{ fill: 'rgb(var(--foreground-rgb) / 0.4)', fontSize: 8, fontFamily: 'monospace' }} 
          />
          <Radar
            name="Alpha Gap"
            dataKey="alpha"
            stroke="#f59e0b"
            fill="#f59e0b"
            fillOpacity={0.3}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#0a0a0b', 
              border: '1px solid rgb(var(--foreground-rgb) / 0.1)',
              fontSize: '10px',
              fontFamily: 'monospace'
            }}
            itemStyle={{ color: '#f59e0b' }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AlphaRadar;
