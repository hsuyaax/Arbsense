function formatTimestamp(ts: string): string {
  try {
    const d = new Date(ts);
    if (Number.isNaN(d.getTime())) return ts;
    return d.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  } catch {
    return ts;
  }
}

const ACTION_MAP: Record<string, string> = {
  scan: "SCAN",
  match: "MATCH",
  opportunity: "EXEC",
  execute: "SEND",
  system: "INIT",
};

export function AgentFeedTab({
  logs,
}: {
  logs: Array<{ timestamp: string; type: string; message: string }>;
}) {
  return (
    <div className="panel">
      <div className="panel-header">
        <span>Agent Execution Feed</span>
        <span>{logs.length} events</span>
      </div>

      {logs.length === 0 ? (
        <p className="text-muted font-mono text-sm py-8 text-center">
          No logs available. Run the agent pipeline first.
        </p>
      ) : (
        <div className="font-mono text-[11px] leading-[1.8] text-muted" style={{ maxHeight: 600, overflow: "auto" }}>
          {logs.map((log, idx) => (
            <div className="flex gap-4 mb-2" key={`log-${idx}`}>
              <span className="text-neutral-600 flex-shrink-0">
                {formatTimestamp(log.timestamp)}
              </span>
              <span className="text-white flex-shrink-0 w-12">
                {ACTION_MAP[log.type] || "SYS"}
              </span>
              <span>{log.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
