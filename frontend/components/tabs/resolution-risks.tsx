import type { MatchRow } from "@/lib/types";

export function ResolutionRisksTab({ matches }: { matches: MatchRow[] }) {
  const rows = matches.filter((m) => m.is_match);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-px bg-white/[0.12] border border-white/[0.12]">
      {/* Main risks table */}
      <div className="panel lg:col-span-8">
        <div className="panel-header">
          <span>Resolution Risk Engine</span>
          <span>{rows.length} matched pairs analyzed</span>
        </div>

        {rows.length === 0 ? (
          <p className="text-muted font-mono text-sm py-8 text-center">
            No matched markets available.
          </p>
        ) : (
          <div>
            <div className="data-row font-mono text-[10px] uppercase text-muted tracking-wide">
              <div>Event</div>
              <div>Platforms</div>
              <div>Similarity</div>
              <div className="text-right">Risk / Verdict</div>
            </div>

            {rows.map((row, idx) => {
              const score = row.resolution_conflict_score ?? 50;
              return (
                <div className="data-row" key={`risk-${idx}`}>
                  <div className="text-[15px] font-normal leading-snug">
                    {row.event_summary || row.market_a.title}
                  </div>
                  <div className="font-mono text-[13px] text-muted">
                    {row.platform_a} vs {row.platform_b}
                  </div>
                  <div className="font-mono text-[13px] text-muted">
                    {(row.embedding_similarity * 100).toFixed(0)}%
                  </div>
                  <div className="flex items-center justify-end gap-3">
                    <span className="font-mono text-[13px] text-white">{score}/100</span>
                    <span className="tag">{row.safety_badge}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Side: Detailed risk breakdown */}
      <div className="panel lg:col-span-4">
        <div className="panel-header">
          <span>Trap Analysis</span>
          <span>AI-Powered</span>
        </div>

        {rows.length > 0 ? (
          <div className="flex flex-col gap-6">
            {rows.slice(0, 3).map((row, idx) => (
              <div key={`detail-${idx}`} className="flex flex-col gap-3 pb-6 border-b border-white/[0.06] last:border-none last:pb-0">
                <div className="flex items-center justify-between">
                  <p className="text-sm text-white">{row.platform_a} × {row.platform_b}</p>
                  <span className="tag">{row.safety_badge}</span>
                </div>

                <div>
                  <span className="font-mono text-[9px] uppercase text-muted tracking-wider">Criteria A</span>
                  <p className="text-[12px] text-muted leading-relaxed mt-0.5">{row.resolution_criteria_a}</p>
                </div>
                <div>
                  <span className="font-mono text-[9px] uppercase text-muted tracking-wider">Criteria B</span>
                  <p className="text-[12px] text-muted leading-relaxed mt-0.5">{row.resolution_criteria_b}</p>
                </div>

                {row.resolution_risks.length > 0 && (
                  <div>
                    <span className="font-mono text-[9px] uppercase text-muted tracking-wider">Risk Factors</span>
                    {row.resolution_risks.map((risk, i) => (
                      <p key={i} className="font-mono text-[11px] text-muted mt-1">— {risk}</p>
                    ))}
                  </div>
                )}

                {row.edge_cases.length > 0 && (
                  <div>
                    <span className="font-mono text-[9px] uppercase text-muted tracking-wider">Edge Cases</span>
                    {row.edge_cases.map((ec, i) => (
                      <p key={i} className="font-mono text-[11px] text-muted mt-1">— {ec}</p>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted font-mono text-sm">Awaiting data...</p>
        )}
      </div>
    </div>
  );
}
