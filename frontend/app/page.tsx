import { DashboardShell } from "@/components/dashboard-shell";
import { Scene } from "@/components/scene";
import {
  fetchChainInfo,
  fetchLogs,
  fetchMarkets,
  fetchMatches,
  fetchOpportunities,
  fetchStats,
} from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function Page() {
  const [stats, markets, matches, opportunitiesRaw, logs, chainInfo] =
    await Promise.all([
      fetchStats(),
      fetchMarkets(),
      fetchMatches(),
      fetchOpportunities(),
      fetchLogs(),
      fetchChainInfo(),
    ]);

  const opportunities = opportunitiesRaw.filter((o) => !o.time_decay_flag);
  const timeValueSpreads = opportunitiesRaw.filter((o) => o.time_decay_flag);

  const uiStats = {
    markets_scanned: stats.markets_scanned,
    platforms: stats.platforms_count,
    ai_matches: stats.matched_pairs,
    opportunities: stats.safe_opportunities,
    time_value_spreads: stats.total_opportunities - stats.safe_opportunities,
    average_spread_pct: stats.avg_spread_pct,
  };

  return (
    <>
      <Scene />
      <main className="relative min-h-screen">
        <DashboardShell
          stats={uiStats}
          markets={markets}
          matches={matches}
          opportunities={opportunities}
          timeValueSpreads={timeValueSpreads}
          logs={logs}
          chainInfo={chainInfo}
        />

        {/* Footer */}
        <footer className="border-t border-border mt-16">
          <div className="mx-auto max-w-[1440px] px-6 md:px-10">
            {/* Main footer */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-10 py-12">
              {/* Brand */}
              <div className="md:col-span-2 flex flex-col gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 border border-white/20 flex items-center justify-center text-[10px] font-mono">
                    AS
                  </div>
                  <span className="text-[18px] font-light tracking-tight">ArbSense</span>
                </div>
                <p className="font-mono text-[11px] text-neutral-500 leading-relaxed max-w-[360px]">
                  AI-powered prediction market intelligence layer on BNB Chain.
                  Find safe arbitrage. Skip the traps. Trust the proof.
                </p>
                <div className="flex items-center gap-3 mt-2">
                  <span className="flex items-center gap-2 font-mono text-[10px] text-muted">
                    <span className="h-1.5 w-1.5 rounded-full bg-green-400 animate-blink" />
                    LIVE ON BSC TESTNET
                  </span>
                </div>
              </div>

              {/* Platform */}
              <div className="flex flex-col gap-3">
                <h4 className="font-mono text-[10px] text-muted uppercase tracking-widest">Platform</h4>
                <div className="flex flex-col gap-2">
                  {["Aggregator", "Opportunities", "Risk Engine", "AI Verification", "On-Chain Proof", "Bets"].map((item) => (
                    <span key={item} className="font-mono text-[11px] text-neutral-500 hover:text-white transition-colors duration-200 cursor-default">
                      {item}
                    </span>
                  ))}
                </div>
              </div>

              {/* Resources */}
              <div className="flex flex-col gap-3">
                <h4 className="font-mono text-[10px] text-muted uppercase tracking-widest">Resources</h4>
                <div className="flex flex-col gap-2">
                  <a
                    href="https://testnet.bscscan.com/address/0x7Ba8FA52dAEd1c1Ea1acEB26E52339946458DeDa"
                    target="_blank"
                    rel="noreferrer"
                    className="font-mono text-[11px] text-neutral-500 hover:text-white transition-colors duration-200"
                  >
                    Smart Contract
                  </a>
                  <a
                    href="https://testnet.bscscan.com/address/0x7Ba8FA52dAEd1c1Ea1acEB26E52339946458DeDa#code"
                    target="_blank"
                    rel="noreferrer"
                    className="font-mono text-[11px] text-neutral-500 hover:text-white transition-colors duration-200"
                  >
                    Verified Source
                  </a>
                  <span className="font-mono text-[11px] text-neutral-500 hover:text-white transition-colors duration-200 cursor-default">
                    API Documentation
                  </span>
                  <span className="font-mono text-[11px] text-neutral-500 hover:text-white transition-colors duration-200 cursor-default">
                    GitHub
                  </span>
                </div>
              </div>
            </div>

            {/* Bottom bar */}
            <div className="border-t border-white/[0.06] py-6 flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-6">
                <p className="font-mono text-[10px] text-neutral-600">
                  Built on BNB Chain
                </p>
                <p className="font-mono text-[10px] text-neutral-700">
                  BSC Testnet + opBNB Testnet
                </p>
              </div>
              <div className="flex items-center gap-6">
                <span className="font-mono text-[10px] text-neutral-700">
                  OpenAI + Claude AI + Web3
                </span>
                <span className="font-mono text-[10px] text-neutral-600">
                  {new Date().getFullYear()} ArbSense
                </span>
              </div>
            </div>
          </div>
        </footer>
      </main>
    </>
  );
}
