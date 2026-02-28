import type { Market } from "@/lib/types";

function qualityBadge(score?: number, grade?: string) {
  const safeScore = typeof score === "number" ? score : 50;
  const label = grade || (safeScore >= 80 ? "A" : safeScore >= 65 ? "B" : safeScore >= 50 ? "C" : "D");
  const cls =
    safeScore >= 80
      ? "bg-green-500/20 text-green-300 border-green-400/30"
      : safeScore >= 65
        ? "bg-blue-500/20 text-blue-300 border-blue-400/30"
        : safeScore >= 50
          ? "bg-yellow-500/20 text-yellow-300 border-yellow-400/30"
          : "bg-red-500/20 text-red-300 border-red-400/30";
  return (
    <span className={`rounded-full border px-2 py-1 text-xs font-semibold ${cls}`}>
      {label} ({safeScore})
    </span>
  );
}

export function AggregatorTab({ markets }: { markets: Market[] }) {
  const grouped = new Map<string, Market[]>();
  for (const market of markets) {
    const key = `${market.category}|${market.resolution_date}`;
    grouped.set(key, [...(grouped.get(key) || []), market]);
  }
  const rows = Array.from(grouped.entries()).slice(0, 25);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-white">Aggregator</h2>
      {rows.length === 0 && <p className="text-slate-400">No market data available.</p>}
      {rows.map(([key, items]) => {
        const best = [...items].sort((a, b) => yesPrice(a) - yesPrice(b))[0];
        return (
          <div key={key} className="rounded-xl border border-line bg-panel p-4">
            <p className="mb-3 text-sm text-slate-400">
              Event Group: <span className="text-slate-200">{key}</span>
            </p>
            <div className="space-y-2">
              {items.map((m) => (
                <div
                  key={`${m.platform}-${m.market_id}`}
                  className={`flex flex-wrap items-center justify-between gap-2 rounded-lg border p-3 ${
                    m.market_id === best.market_id
                      ? "border-green-400/40 bg-green-500/10"
                      : "border-white/10 bg-white/5"
                  }`}
                >
                  <div>
                    <p className="font-medium text-white">{m.title}</p>
                    <p className="text-xs text-slate-400">{m.platform}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {qualityBadge(m.quality_score, m.quality_grade)}
                    <span className="mono text-cyan-300">YES ${yesPrice(m).toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function yesPrice(market: Market) {
  return market.outcomes.find((o) => o.name.toLowerCase() === "yes")?.price ?? 0;
}
