import type { OpportunityRow } from "@/lib/types";
import { Accordion } from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

function riskBadge(verdict?: string) {
  if (verdict === "SAFE") return "safe";
  if (verdict === "DANGER") return "danger";
  return "caution";
}

export function SafeOpportunitiesTab({
  opportunities,
  timeValueSpreads
}: {
  opportunities: OpportunityRow[];
  timeValueSpreads: OpportunityRow[];
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-white">Safe Opportunities</h2>
      {opportunities.length === 0 && (
        <p className="text-slate-400">No opportunities available. Run the agent pipeline first.</p>
      )}
      {opportunities.map((opp, idx) => (
        <Card key={`${opp.event_summary}-${idx}`}>
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <p className="font-semibold text-white">{opp.event_summary}</p>
            <Badge variant={riskBadge(opp.safety_badge) as "safe" | "danger" | "caution"}>
              {opp.safety_badge || "CAUTION"}
            </Badge>
          </div>
          <div className="grid grid-cols-1 gap-2 text-sm md:grid-cols-4">
            <p>Spread: <span className="mono text-cyan-300">{opp.spread_pct.toFixed(2)}%</span></p>
            <p>Profit: <span className="mono text-green-300">{opp.profit_pct.toFixed(2)}%</span></p>
            <p>Score: <span className="mono">{opp.score.toFixed(3)}</span></p>
            <p>Confidence: <span className="mono">{opp.ai_confidence.toFixed(3)}</span></p>
          </div>
          <p className="mt-2 text-sm text-slate-300">{opp.action}</p>
          <div className="mt-3">
            <Accordion title="AI reasoning">
            <p className="mt-2 text-sm text-slate-300">{opp.reasoning}</p>
            {opp.resolution_risks.length > 0 && (
              <p className="mt-2 text-sm text-yellow-300">
                Risks: {opp.resolution_risks.join(" | ")}
              </p>
            )}
            </Accordion>
          </div>
        </Card>
      ))}

      <div className="mt-8 space-y-3">
        <h3 className="text-lg font-semibold text-yellow-300">Time-Value Spreads (Not Arbitrage)</h3>
        {timeValueSpreads.length === 0 && (
          <p className="text-slate-400">No time-value spreads detected.</p>
        )}
        {timeValueSpreads.map((opp, idx) => (
          <Card key={`${opp.event_summary}-tv-${idx}`} className="border-yellow-400/20 bg-yellow-500/10">
            <p className="font-medium text-white">{opp.event_summary}</p>
            <p className="mt-1 text-sm text-slate-300">
              Resolution timelines differ by more than 7 days; treat as time premium, not pure arbitrage.
            </p>
          </Card>
        ))}
      </div>
    </div>
  );
}
