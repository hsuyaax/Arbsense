import type { MatchRow } from "@/lib/types";

export function AiAnalysisTab({ matches }: { matches: MatchRow[] }) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-white">AI Analysis</h2>
      {matches.length === 0 && <p className="text-slate-400">No verification data available.</p>}
      {matches.map((row, idx) => (
        <details key={`${row.market_a.market_id}-${row.market_b.market_id}-${idx}`} className="rounded-xl border border-line bg-panel p-4">
          <summary className="cursor-pointer">
            <span className="font-medium text-white">{row.market_a.title}</span>
            <span className="mx-2 text-slate-400">vs</span>
            <span className="font-medium text-white">{row.market_b.title}</span>
            <span className="ml-3 text-xs text-slate-400">
              confidence {row.confidence.toFixed(3)}
            </span>
          </summary>
          <div className="mt-3 space-y-2 text-sm">
            <p className="text-slate-300">{row.reasoning}</p>
            <p className="text-slate-400">
              Quality A: {row.market_a.quality_score ?? 50} ({row.market_a.quality_grade ?? "C"}) -
              {" "}{row.market_a.quality_reasoning ?? "n/a"}
            </p>
            <p className="text-slate-400">
              Quality B: {row.market_b.quality_score ?? 50} ({row.market_b.quality_grade ?? "C"}) -
              {" "}{row.market_b.quality_reasoning ?? "n/a"}
            </p>
            <p className="text-slate-400">
              Resolution Conflict: {row.resolution_conflict_score ?? 50} | Verdict:{" "}
              {row.safety_badge ?? "CAUTION"}
            </p>
            <pre className="overflow-auto rounded bg-black/30 p-2 text-xs text-slate-300">
              {JSON.stringify(row.outcome_mapping, null, 2)}
            </pre>
          </div>
        </details>
      ))}
    </div>
  );
}
