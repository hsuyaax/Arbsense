export function AgentFeedTab({
  logs
}: {
  logs: Array<{ timestamp: string; type: string; message: string }>;
}) {
  const color: Record<string, string> = {
    scan: "border-blue-400/40 text-blue-200",
    match: "border-green-400/40 text-green-200",
    opportunity: "border-yellow-400/40 text-yellow-200",
    execute: "border-red-400/40 text-red-200",
    system: "border-slate-500/40 text-slate-200"
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-white">Agent Feed</h2>
      <div className="max-h-[600px] space-y-2 overflow-auto pr-1">
        {logs.length === 0 && <p className="text-slate-400">No logs available.</p>}
        {logs.map((log, idx) => (
          <div
            key={`${log.timestamp}-${idx}`}
            className={`rounded-lg border-l-4 bg-panel p-3 mono text-sm ${color[log.type] || color.system}`}
          >
            <p className="text-xs text-slate-400">{log.timestamp}</p>
            <p>[{log.type}] {log.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
