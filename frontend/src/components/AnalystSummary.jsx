
import React from 'react';
import { AlertTriangle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const AnalystSummary = ({ briefing }) => (
  <div className="terminal-card bg-bg1/40 border-white/5 p-4">
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

export default AnalystSummary;
