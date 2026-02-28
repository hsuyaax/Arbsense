type Props = {
  stats: {
    markets_scanned: number;
    platforms: number;
    ai_matches: number;
    opportunities: number;
    time_value_spreads?: number;
    average_spread_pct: number;
  };
};

export function Header({ stats }: Props) {
  return (
    <section className="py-8 md:py-12 flex flex-col md:flex-row justify-between items-start gap-8 animate-fade-in-up">
      <div className="flex flex-col gap-4">
        <h1 className="text-4xl md:text-[56px] font-light leading-[1.08] tracking-[-2px] max-w-[700px]">
          Intelligence for{" "}
          <span className="text-muted">Cross-Platform</span>{" "}
          Prediction Markets
        </h1>
        <p className="font-mono text-[12px] text-neutral-500 max-w-[520px] leading-relaxed">
          AI-powered arbitrage detection across {stats.platforms} platforms. Semantic matching.
          Resolution risk analysis. On-chain proof.
        </p>
      </div>

      <div className="flex flex-col gap-3 shrink-0">
        <div className="font-mono text-[11px] flex items-center gap-2 px-4 py-2 border border-border whitespace-nowrap hover:border-white/25 transition-colors duration-300">
          <span className="w-1.5 h-1.5 bg-white rounded-full animate-blink" />
          SYSTEM ACTIVE
        </div>
        <div className="font-mono text-[10px] text-neutral-600 text-right">
          {stats.markets_scanned} markets / {stats.ai_matches} matches / {stats.opportunities} opps
        </div>
      </div>
    </section>
  );
}
