import type { MatchRow } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

function scoreClass(score: number) {
  if (score < 30) return "text-green-300 border-green-400/30 bg-green-500/10";
  if (score > 70) return "text-red-300 border-red-400/30 bg-red-500/10";
  return "text-yellow-300 border-yellow-400/30 bg-yellow-500/10";
}

function verdictIcon(verdict?: string) {
  if (verdict === "SAFE") return "SAFE";
  if (verdict === "DANGER") return "DANGER";
  return "CAUTION";
}

function verdictVariant(verdict?: string): "safe" | "caution" | "danger" {
  if (verdict === "SAFE") return "safe";
  if (verdict === "DANGER") return "danger";
  return "caution";
}

export function ResolutionRisksTab({ matches }: { matches: MatchRow[] }) {
  const rows = matches.filter((m) => m.is_match);
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-white">Resolution Risks</h2>
      {rows.length === 0 && <p className="text-slate-400">No matched markets available.</p>}
      {rows.map((row, idx) => {
        const score = row.resolution_conflict_score ?? 50;
        const dateGap = getDateGapDays(row.market_a.resolution_date, row.market_b.resolution_date);
        return (
          <Card key={`${row.market_a.market_id}-${row.market_b.market_id}-${idx}`}>
            <p className="mb-3 font-semibold text-white">{row.event_summary || row.market_a.title}</p>
            <div className="grid grid-cols-1 gap-3 md:grid-cols-[1fr_auto_1fr]">
              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <p className="text-sm font-medium text-slate-200">{row.market_a.platform}</p>
                <p className="mt-1 text-sm text-slate-300">{row.market_a.description}</p>
              </div>
              <div className={`flex items-center justify-center rounded-full border px-4 text-lg font-bold mono ${scoreClass(score)}`}>
                {score}
              </div>
              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <p className="text-sm font-medium text-slate-200">{row.market_b.platform}</p>
                <p className="mt-1 text-sm text-slate-300">{row.market_b.description}</p>
              </div>
            </div>
            <p className="mt-2 text-xs text-slate-400">
              Verdict: <Badge variant={verdictVariant(row.safety_badge)}>{verdictIcon(row.safety_badge)}</Badge>
              {typeof dateGap === "number" && (
                <>
                  {" "} | Date gap: <span className="mono">{dateGap} days</span>
                </>
              )}
            </p>
            <div className="mt-3 rounded-lg border border-red-400/20 bg-red-500/10 p-3">
              <p className="text-sm font-semibold text-red-300">AI Trap Warnings</p>
              <p className="mt-1 text-sm text-slate-300">
                {row.resolution_risks.join(" | ") || row.reasoning}
              </p>
            </div>
          </Card>
        );
      })}
    </div>
  );
}

function getDateGapDays(dateA?: string, dateB?: string): number | null {
  if (!dateA || !dateB) return null;
  const a = new Date(dateA);
  const b = new Date(dateB);
  if (Number.isNaN(a.getTime()) || Number.isNaN(b.getTime())) return null;
  return Math.abs(Math.round((a.getTime() - b.getTime()) / (1000 * 60 * 60 * 24)));
}
