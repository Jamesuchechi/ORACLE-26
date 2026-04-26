
import React from 'react';
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, Radar } from 'recharts';

const SignalRadar = ({ data }) => {
  if (!data) return null;

  // Expected data format: { sports: 0.8, markets: 0.5, ... }
  const chartData = [
    { subject: 'Sports', A: data.sports || 0, fullMark: 1 },
    { subject: 'Markets', A: data.markets || 0, fullMark: 1 },
    { subject: 'Finance', A: data.finance || 0, fullMark: 1 },
    { subject: 'Climate', A: data.climate || 0, fullMark: 1 },
    { subject: 'Social', A: data.social || 0, fullMark: 1 },
  ];

  return (
    <div className="h-32 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
          <PolarGrid stroke="rgb(var(--foreground-rgb) / 0.05)" />
          <PolarAngleAxis 
            dataKey="subject" 
            tick={{ fill: 'rgb(var(--foreground-rgb) / 0.6)', fontSize: 7, fontFamily: 'monospace' }} 
          />
          <Radar
            name="Signals"
            dataKey="A"
            stroke="#f59e0b"
            fill="#f59e0b"
            fillOpacity={0.2}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SignalRadar;
