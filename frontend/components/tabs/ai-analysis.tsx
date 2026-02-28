import type { MatchRow } from "@/lib/types";

export function AiAnalysisTab({ matches }: { matches: MatchRow[] }) {
  const verified = matches.filter((m) => m.is_match);
  const rejected = matches.filter((m) => !m.is_match);

  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-px bg-white/[0.12] border border-white/[0.12]">
        {/* Verified matches table */}
        <div className="panel lg:col-span-8">
          <div className="panel-header">
            <span>Claude Verification — Verified Matches</span>
            <span>Model: SONNET</span>
          </div>

          {verified.length === 0 ? (
            <p className="text-muted font-mono text-sm py-8 text-center">
              No verification data available.
            </p>
          ) : (
            <div>
              <div className="data-row font-mono text-[10px] uppercase text-muted tracking-wide">
                <div>Event</div>
                <div>Platforms</div>
                <div>Confidence</div>
                <div className="text-right">Verdict</div>
              </div>

              {verified.map((row, idx) => (
                <div className="data-row" key={`match-${idx}`}>
                  <div className="text-[15px] font-normal leading-snug">
                    {row.event_summary || row.market_a.title}
                  </div>
                  <div className="font-mono text-[13px] text-muted">
                    {row.platform_a} × {row.platform_b}
                  </div>
                  <div className="font-mono text-[13px] text-white">
                    {(row.confidence * 100).toFixed(1)}%
                  </div>
                  <div className="text-right">
                    <span className="tag">{row.safety_badge}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* AI Reasoning terminal */}
        <div className="panel lg:col-span-4">
          <div className="panel-header">
            <span>Reasoning Log</span>
            <span>Live</span>
          </div>

          <div className="font-mono text-[11px] leading-[1.8] text-muted overflow-hidden relative" style={{ maxHeight: 400 }}>
            {verified.slice(0, 6).map((row, idx) => (
              <div key={`term-${idx}`} className="mb-4">
                <div className="flex gap-4 mb-1">
                  <span className="text-neutral-600">{String(idx + 1).padStart(2, "0")}</span>
                  <span className="text-white">EVAL</span>
                  <span>{row.platform_a} × {row.platform_b}</span>
                </div>
                <div className="flex gap-4 mb-1">
                  <span className="text-neutral-600">{"  "}</span>
                  <span className="text-white">PASS</span>
                  <span>Confidence: {(row.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="flex gap-4">
                  <span className="text-neutral-600">{"  "}</span>
                  <span className="text-[10px] leading-relaxed">{row.reasoning}</span>
                </div>
              </div>
            ))}
            {/* Fade overlay */}
            <div className="absolute bottom-0 left-0 w-full h-16 bg-gradient-to-t from-[#0a0a0a] to-transparent pointer-events-none" />
          </div>
        </div>
      </div>

      {/* Rejected pairs */}
      {rejected.length > 0 && (
        <div className="panel">
          <div className="panel-header">
            <span>Rejected Pairs — {rejected.length} discarded</span>
            <span>0 0 1 0 1 1 0 0</span>
          </div>
          {rejected.map((row, idx) => (
            <div className="data-row opacity-50" key={`reject-${idx}`}>
              <div className="text-[15px] font-normal">
                {row.event_summary || row.market_a.title}
              </div>
              <div className="font-mono text-[13px] text-muted">
                {row.platform_a} × {row.platform_b}
              </div>
              <div className="font-mono text-[13px] text-muted">
                {(row.confidence * 100).toFixed(0)}%
              </div>
              <div className="font-mono text-[13px] text-muted text-right">Rejected</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
