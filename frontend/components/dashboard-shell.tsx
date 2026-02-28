"use client";

import { useMemo, useState } from "react";
import { AggregatorTab } from "@/components/tabs/aggregator";
import { AgentFeedTab } from "@/components/tabs/agent-feed";
import { AiAnalysisTab } from "@/components/tabs/ai-analysis";
import { OnChainTab } from "@/components/tabs/on-chain";
import { ResolutionRisksTab } from "@/components/tabs/resolution-risks";
import { SafeOpportunitiesTab } from "@/components/tabs/safe-opportunities";
import { Header } from "@/components/header";
import { Tabs } from "@/components/ui/tabs";
import type { MatchRow, Market, OpportunityRow } from "@/lib/types";

const TAB_NAMES = [
  "Aggregator",
  "Safe Opportunities",
  "Resolution Risks",
  "AI Analysis",
  "Agent Feed",
  "On-Chain"
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
  const render = useMemo(() => {
    if (active === "Aggregator") return <AggregatorTab markets={props.markets} />;
    if (active === "Safe Opportunities") {
      return (
        <SafeOpportunitiesTab
          opportunities={props.opportunities}
          timeValueSpreads={props.timeValueSpreads}
        />
      );
    }
    if (active === "Resolution Risks") return <ResolutionRisksTab matches={props.matches} />;
    if (active === "AI Analysis") return <AiAnalysisTab matches={props.matches} />;
    if (active === "Agent Feed") return <AgentFeedTab logs={props.logs} />;
    return <OnChainTab chainInfo={props.chainInfo} />;
  }, [
    active,
    props.markets,
    props.matches,
    props.opportunities,
    props.timeValueSpreads,
    props.logs,
    props.chainInfo
  ]);

  return (
    <main className="min-h-screen bg-bg px-4 py-6 text-slate-100 md:px-8">
      <Header stats={props.stats} />

      <Tabs tabs={TAB_NAMES} active={active} onChange={(t) => setActive(t as TabName)} />

      {render}
    </main>
  );
}
