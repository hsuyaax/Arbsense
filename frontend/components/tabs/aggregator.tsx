import type { Market } from "@/lib/types";

function yesPrice(market: Market) {
  return market.outcomes.find((o) => o.name.toLowerCase() === "yes")?.price ?? 0;
}

function noPrice(market: Market) {
  return market.outcomes.find((o) => o.name.toLowerCase() === "no")?.price ?? 0;
}

function totalLiquidity(market: Market) {
  return market.outcomes.reduce((sum, o) => sum + (o.liquidity || 0), 0);
}

export function AggregatorTab({ markets }: { markets: Market[] }) {
  const sorted = [...markets].sort((a, b) => (b.quality_score ?? 0) - (a.quality_score ?? 0));
  const platforms = new Set(markets.map((m) => m.platform)).size;

  return (
    <div className="panel">
      <div className="panel-header">
        <span>Active Market Index — {markets.length} markets across {platforms} platforms</span>
        <span>1 1 0 1 0 0 1 1</span>
      </div>

      {sorted.length === 0 ? (
        <p className="text-muted font-mono text-sm py-8 text-center">
          No market data available. Run the agent pipeline first.
        </p>
      ) : (
        <div>
          {/* Header row */}
          <div className="data-row font-mono text-[10px] uppercase text-muted tracking-wide">
            <div>Market Target</div>
            <div>Platform</div>
            <div>Yes / No</div>
            <div className="text-right">Liquidity</div>
          </div>

          {sorted.map((m) => (
            <div className="data-row" key={`${m.platform}-${m.market_id}`}>
              <div>
                <p className="text-[15px] font-normal leading-snug">{m.title}</p>
                <div className="flex items-center gap-2 mt-1.5">
                  {m.category && <span className="tag">{m.category}</span>}
                  <span className="tag">{m.quality_grade || "C"}</span>
                </div>
              </div>
              <div className="font-mono text-[13px] text-muted">{m.platform}</div>
              <div className="font-mono text-[13px]">
                <span className="text-white">¢{(yesPrice(m) * 100).toFixed(1)}</span>
                <span className="text-muted mx-1">/</span>
                <span className="text-muted">¢{(noPrice(m) * 100).toFixed(1)}</span>
              </div>
              <div className="font-mono text-[13px] text-muted text-right">
                ${new Intl.NumberFormat("en-US").format(totalLiquidity(m))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
