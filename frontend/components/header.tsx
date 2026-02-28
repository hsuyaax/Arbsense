type Stats = {
  markets_scanned: number;
  platforms: number;
  ai_matches: number;
  opportunities: number;
  time_value_spreads?: number;
  average_spread_pct: number;
};

export function Header({ stats }: { stats: Stats }) {
  const cards = [
    { label: "Markets Scanned", value: stats.markets_scanned },
    { label: "Platforms", value: stats.platforms },
    { label: "AI Matches", value: stats.ai_matches },
    { label: "Safe Opportunities", value: stats.opportunities },
    { label: "Time-Value Spreads", value: stats.time_value_spreads ?? 0 },
    { label: "Avg Spread %", value: `${stats.average_spread_pct.toFixed(2)}%` }
  ];

  return (
    <div className="mb-6 rounded-2xl border border-line bg-hero-shader p-6 shadow-glow">
      <h1 className="mb-2 bg-gradient-to-r from-cyan-300 to-violet-400 bg-clip-text text-3xl font-bold text-transparent">
        ArbSense
      </h1>
      <p className="mb-5 text-sm text-slate-300">
        Prediction Market Intelligence Layer for BNB Chain
      </p>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-6">
        {cards.map((card) => (
          <div
            key={card.label}
            className="rounded-xl border border-white/10 bg-white/5 p-3 backdrop-blur-xl"
          >
            <p className="text-xs uppercase tracking-wide text-slate-400">{card.label}</p>
            <p className="mt-1 text-xl font-semibold text-white mono">{card.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
