import type { OpportunityRow } from "@/lib/types";

export function SafeOpportunitiesTab({
  opportunities,
  timeValueSpreads,
}: {
  opportunities: OpportunityRow[];
  timeValueSpreads: OpportunityRow[];
}) {
  return (
    <div className="flex flex-col gap-6">
      {/* Main grid: table + details side panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-px bg-white/[0.12] border border-white/[0.12]">
        {/* Opportunities table - 8 cols */}
        <div className="panel lg:col-span-8">
          <div className="panel-header">
            <span>Active Spread Discoveries</span>
            <span>{opportunities.length} found</span>
          </div>

          {opportunities.length === 0 ? (
            <p className="text-muted font-mono text-sm py-8 text-center">
              No opportunities available. Run the agent pipeline first.
            </p>
          ) : (
            <div>
              <div className="data-row font-mono text-[10px] uppercase text-muted tracking-wide">
                <div>Market Target</div>
                <div>Platform A</div>
                <div>Platform B</div>
                <div className="text-right">Net Spread</div>
              </div>

              {opportunities.map((opp, idx) => (
                <div className="data-row" key={`opp-${idx}`}>
                  <div className="text-[15px] font-normal leading-snug">{opp.event_summary}</div>
                  <div className="font-mono text-[13px] text-muted">
                    {opp.market_a.platform} ¢{(opp.market_a.yes_price * 100).toFixed(1)}
                  </div>
                  <div className="font-mono text-[13px] text-muted">
                    {opp.market_b.platform} ¢{(opp.market_b.yes_price * 100).toFixed(1)}
                  </div>
                  <div className="font-mono text-[13px] text-white text-right">
                    +{opp.spread_pct.toFixed(2)}%
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Details side panel - 4 cols */}
        <div className="panel lg:col-span-4">
          <div className="panel-header">
            <span>Economics Detail</span>
            <span>AI Verified</span>
          </div>

          {opportunities.length > 0 ? (
            <div className="flex flex-col gap-6">
              {opportunities.slice(0, 3).map((opp, idx) => (
                <div key={`detail-${idx}`} className="flex flex-col gap-3 pb-6 border-b border-white/[0.06] last:border-none last:pb-0">
                  <p className="text-sm text-white font-normal">{opp.event_summary}</p>
                  <div className="flex justify-between">
                    <span className="font-mono text-[10px] uppercase text-muted">Net Profit</span>
                    <span className="font-mono text-[13px] text-white">+{opp.profit_pct.toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-mono text-[10px] uppercase text-muted">AI Confidence</span>
                    <span className="font-mono text-[13px] text-white">{(opp.ai_confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-mono text-[10px] uppercase text-muted">Risk Score</span>
                    <span className="font-mono text-[13px] text-white">{opp.resolution_conflict_score}/100</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-[10px] uppercase text-muted">Verdict</span>
                    <span className="tag">{opp.safety_badge}</span>
                  </div>
                  <p className="font-mono text-[11px] text-muted leading-relaxed">{opp.action}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted font-mono text-sm">Awaiting data...</p>
          )}
        </div>
      </div>

      {/* Time-Value Spreads */}
      {timeValueSpreads.length > 0 && (
        <div className="panel">
          <div className="panel-header">
            <span>Time-Value Spreads (not pure arbitrage)</span>
            <span>{timeValueSpreads.length} detected</span>
          </div>
          {timeValueSpreads.map((opp, idx) => (
            <div className="data-row" key={`tv-${idx}`}>
              <div className="text-[15px] font-normal text-muted">{opp.event_summary}</div>
              <div className="font-mono text-[13px] text-muted">Spread: {opp.spread_pct.toFixed(2)}%</div>
              <div className="font-mono text-[13px] text-muted">Conf: {(opp.ai_confidence * 100).toFixed(0)}%</div>
              <div className="font-mono text-[13px] text-muted text-right">Time Premium</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
