import React from "react";
import { motion } from "framer-motion";
import { CloudRain } from "lucide-react";

const VenueRiskGrid = ({ venues }) => {
  return (
    <div className="terminal-card bg-bg1/40 border-border">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-[10px] font-mono font-bold text-muted tracking-[0.2em] uppercase flex items-center gap-2">
          <CloudRain size={12} className="text-red" /> Venue Stress Map
        </h3>
        <span className="text-[9px] font-mono text-muted">
          16 HOST CITIES
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {(venues || []).slice(0, 8).map((venue) => (
          <div
            key={venue.venue}
            className="p-3 rounded-lg bg-[var(--card-bg)] border border-border space-y-2 relative overflow-hidden group"
          >
            {/* Background Risk Pulse */}
            {venue.risk_score > 0.6 && (
              <div className="absolute inset-0 bg-red/5 animate-pulse pointer-events-none" />
            )}

            <div className="flex justify-between items-start relative z-10">
              <div>
                <p className="text-[11px] font-bold tracking-tight">
                  {venue.city}
                </p>
                <p className="text-[8px] font-mono text-muted uppercase">
                  {venue.venue}
                </p>
              </div>
              <div
                className={`text-[8px] font-mono px-1.5 py-0.5 rounded ${
                  venue.status === "CRITICAL"
                    ? "bg-red/20 text-red"
                    : venue.status === "WARNING"
                      ? "bg-amber/20 text-amber"
                      : "bg-teal/20 text-teal"
                }`}
              >
                {venue.status}
              </div>
            </div>

            <div className="flex items-center gap-4 relative z-10">
              <div className="flex-1 space-y-1">
                <div className="flex justify-between text-[8px] font-mono text-muted uppercase">
                  <span>Stress Level</span>
                  <span>{(venue.risk_score * 100).toFixed(0)}%</span>
                </div>
                <div className="h-1 bg-foreground/30 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(venue.risk_score || 0) * 100}%` }}
                    className={`h-full ${venue.risk_score > 0.6 ? "bg-red" : "bg-amber"} opacity-90 dark:opacity-60`}
                  />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 pt-4 border-t border-border">
        <div className="flex items-center gap-6 text-[9px] font-mono tracking-widest uppercase">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-red shadow-[0_0_8px_rgba(239,68,68,0.6)] animate-pulse" />
            <span className="text-foreground/60">Extreme Alt/Heat</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-amber shadow-[0_0_8px_rgba(245,158,11,0.6)]" />
            <span className="text-muted">Moderate Stress</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-teal shadow-[0_0_8px_rgba(20,184,166,0.6)]" />
            <span className="text-muted">Climate Stable</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VenueRiskGrid;
