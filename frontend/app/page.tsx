import { DashboardShell } from "@/components/dashboard-shell";
import {
  fetchChainInfo,
  fetchLogs,
  fetchMarkets,
  fetchMatches,
  fetchOpportunities,
  fetchStats
} from "@/lib/api";

export default async function Page() {
  const [stats, markets, matches, opportunitiesRaw, logs, chainInfo] =
    await Promise.all([
      fetchStats(),
      fetchMarkets(),
      fetchMatches(),
      fetchOpportunities(),
      fetchLogs(),
      fetchChainInfo()
    ]);

  const opportunities = opportunitiesRaw.filter((o) => !o.time_decay_flag);
  const timeValueSpreads = opportunitiesRaw.filter((o) => o.time_decay_flag);

  const uiStats = {
    markets_scanned: stats.markets_scanned,
    platforms: stats.platforms_count,
    ai_matches: stats.matched_pairs,
    opportunities: stats.safe_opportunities,
    time_value_spreads: stats.total_opportunities - stats.safe_opportunities,
    average_spread_pct: stats.avg_spread_pct
  };

  return (
    <DashboardShell
      stats={uiStats}
      markets={markets}
      matches={matches}
      opportunities={opportunities}
      timeValueSpreads={timeValueSpreads}
      logs={logs}
      chainInfo={chainInfo}
    />
  );
}
