import React from 'react';
import { 
  Radar, RadarChart, PolarGrid, 
  PolarAngleAxis, ResponsiveContainer 
} from 'recharts';

const SignalRadar = ({ data }) => {
  // Map the team signal data to Recharts format
  const chartData = [
    { subject: 'Sports', A: data.sports * 100, fullMark: 100 },
    { subject: 'Markets', A: data.markets * 100, fullMark: 100 },
    { subject: 'Finance', A: data.finance * 100, fullMark: 100 },
    { subject: 'Climate', A: data.climate * 100, fullMark: 100 },
    { subject: 'Social', A: data.social * 100, fullMark: 100 },
  ];

  return (
    <div className="h-48 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
          <PolarGrid stroke="#ffffff10" />
          <PolarAngleAxis 
            dataKey="subject" 
            tick={{ fill: '#ffffff40', fontSize: 8, fontFamily: 'monospace' }}
          />
          <Radar
            name="Signals"
            dataKey="A"
            stroke="#f59e0b"
            fill="#f59e0b"
            fillOpacity={0.3}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SignalRadar;
