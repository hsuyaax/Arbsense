"use client";

import { useMemo, useState, useCallback } from "react";
import { AggregatorTab } from "@/components/tabs/aggregator";
import { AgentFeedTab } from "@/components/tabs/agent-feed";
import { AiAnalysisTab } from "@/components/tabs/ai-analysis";
import { OnChainTab } from "@/components/tabs/on-chain";
import { ResolutionRisksTab } from "@/components/tabs/resolution-risks";
import { SafeOpportunitiesTab } from "@/components/tabs/safe-opportunities";
import { FunBetsTab } from "@/components/tabs/fun-bets";
import { Header } from "@/components/header";
import { Navbar } from "@/components/navbar";
import { useLiveStream } from "@/lib/use-live-stream";
import type { MatchRow, Market, OpportunityRow } from "@/lib/types";

const TAB_NAMES = [
  "Aggregator",
  "Opportunities",
  "Risks",
  "Verification",
  "Agent Feed",
  "Infrastructure",
  "Bets",
] as const;

type TabName = (typeof TAB_NAMES)[number];

type Props = {
  stats: {
    markets_scanned: number;
    platforms: number;
    ai_matches: number;
    opportunities: number;
    time_value_spreads?: number;
    average_spread_pct: number;
  };
  markets: Market[];
  matches: MatchRow[];
  opportunities: OpportunityRow[];
  timeValueSpreads: OpportunityRow[];
  logs: Array<{ timestamp: string; type: string; message: string }>;
  chainInfo: {
    bsc: {
      contract_address: string;
      explorer_url: string;
      verified: boolean;
      opportunity_count: number;
      network: string;
    };
    opbnb: {
      contract_address: string;
      explorer_url: string;
      verified: boolean;
      opportunity_count: number;
      network: string;
    };
    wallet_address: string;
    wallet_balance_bsc: string;
    wallet_balance_opbnb: string;
  };
};

export function DashboardShell(props: Props) {
  const [active, setActive] = useState<TabName>("Aggregator");
  const [tabKey, setTabKey] = useState(0);
  const { live, connected, triggerRefresh } = useLiveStream();

  const handleTabChange = useCallback((t: string) => {
    setActive(t as TabName);
    setTabKey((k) => k + 1);
  }, []);

  const render = useMemo(() => {
    switch (active) {
      case "Aggregator":
        return <AggregatorTab markets={props.markets} />;
      case "Opportunities":
        return (
          <SafeOpportunitiesTab
            opportunities={props.opportunities}
            timeValueSpreads={props.timeValueSpreads}
          />
        );
      case "Risks":
        return <ResolutionRisksTab matches={props.matches} />;
      case "Verification":
        return <AiAnalysisTab matches={props.matches} />;
      case "Agent Feed":
        return <AgentFeedTab logs={props.logs} />;
      case "Infrastructure":
        return <OnChainTab chainInfo={props.chainInfo} />;
      case "Bets":
        return <FunBetsTab />;
    }
  }, [
    active,
    props.markets,
    props.matches,
    props.opportunities,
    props.timeValueSpreads,
    props.logs,
    props.chainInfo,
  ]);

  return (
    <div className="max-w-[1440px] mx-auto px-6 md:px-10 py-6 flex flex-col gap-8 min-h-screen">
      <Navbar tabs={TAB_NAMES} active={active} onChange={handleTabChange} />
      <Header stats={props.stats} />

      {/* Live Status Bar */}
      <div className="flex items-center justify-between animate-fade-in" style={{ animationDelay: "200ms" }}>
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-2 font-mono text-[11px] text-muted">
            <span className={`w-1.5 h-1.5 rounded-full transition-colors duration-500 ${connected ? "bg-green-400 animate-blink" : "bg-neutral-600"}`} />
            {connected ? "LIVE STREAM CONNECTED" : "CONNECTING..."}
          </span>
          {live && (
            <span className="font-mono text-[11px] text-neutral-600 animate-fade-in">
              {live.markets_scanned} markets · {live.opportunities} opps · {live.avg_spread.toFixed(2)}% avg
            </span>
          )}
        </div>
        <button
          onClick={triggerRefresh}
          className="font-mono text-[11px] text-muted hover:text-white border border-white/[0.12] hover:border-white/40 px-4 py-1.5 bg-transparent cursor-pointer transition-all duration-200 hover:-translate-y-px active:translate-y-0"
        >
          ↻ Refresh
        </button>
      </div>

      {/* Metrics Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-white/[0.12] border border-white/[0.12] stagger-children">
        <div className="panel flex flex-col gap-2">
          <div className="font-mono text-[10px] uppercase tracking-widest text-muted">Markets Indexed</div>
          <div className="font-mono text-2xl tabular-nums">{live?.markets_scanned ?? props.stats.markets_scanned}</div>
          <div className="font-mono text-[10px] text-neutral-600">{props.stats.platforms} platforms live</div>
        </div>
        <div className="panel flex flex-col gap-2">
          <div className="font-mono text-[10px] uppercase tracking-widest text-muted">AI-Verified Matches</div>
          <div className="font-mono text-2xl tabular-nums">{props.stats.ai_matches}</div>
          <div className="font-mono text-[10px] text-neutral-600">Claude semantic matching</div>
        </div>
        <div className="panel flex flex-col gap-2">
          <div className="font-mono text-[10px] uppercase tracking-widest text-muted">Safe Opportunities</div>
          <div className="font-mono text-2xl tabular-nums">{live?.opportunities ?? props.stats.opportunities}</div>
          <div className="font-mono text-[10px] text-neutral-600">up to {(live?.avg_spread ?? props.stats.average_spread_pct).toFixed(1)}% spread</div>
        </div>
        <div className="panel flex flex-col gap-2">
          <div className="font-mono text-[10px] uppercase tracking-widest text-muted">On-Chain Reports</div>
          <div className="font-mono text-2xl tabular-nums">{props.chainInfo.bsc.opportunity_count}</div>
          <div className="font-mono text-[10px] text-neutral-600">BSC Testnet deployed</div>
        </div>
      </div>

      {/* USP Feature Strip */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-px bg-white/[0.06] border border-white/[0.06] stagger-children">
        {[
          ["01", "LIVE DATA", "Polymarket + Kalshi APIs"],
          ["02", "AI MATCHING", "Claude semantic verification"],
          ["03", "RISK ENGINE", "Resolution trap detection"],
          ["04", "ON-CHAIN", "Immutable proof on BNB Chain"],
          ["05", "REAL-TIME", "SSE streaming + live refresh"],
        ].map(([num, title, desc]) => (
          <div key={num} className="px-5 py-4 bg-panel/50 hover:bg-panel transition-colors duration-200 cursor-default group">
            <span className="font-mono text-[9px] text-neutral-700 group-hover:text-neutral-500 transition-colors">{num}</span>
            <div className="font-mono text-[11px] text-white mt-1">{title}</div>
            <div className="font-mono text-[9px] text-neutral-600 mt-0.5">{desc}</div>
          </div>
        ))}
      </div>

      {/* Tab Content with transition */}
      <div key={tabKey} className="animate-fade-in-up min-h-[400px]">
        {render}
      </div>
    </div>
  );
}
