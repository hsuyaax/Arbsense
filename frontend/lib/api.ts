import type { MatchRow, Market, OpportunityRow } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const res = await fetch(`${API_URL}${path}`, { cache: "no-store" });
    if (!res.ok) {
      return fallback;
    }
    return (await res.json()) as T;
  } catch {
    return fallback;
  }
}

export async function fetchMarkets() {
  return getJson<Market[]>("/markets", []);
}

export async function fetchMatches() {
  return getJson<MatchRow[]>("/matches", []);
}

export async function fetchOpportunities() {
  return getJson<OpportunityRow[]>("/opportunities", []);
}

export async function fetchLogs() {
  return getJson<Array<{ timestamp: string; type: string; message: string }>>("/logs", []);
}

export async function fetchStats() {
  return getJson<{
    markets_scanned: number;
    platforms_count: number;
    platform_names: string[];
    matched_pairs: number;
    total_opportunities: number;
    safe_opportunities: number;
    caution_opportunities: number;
    danger_opportunities: number;
    avg_spread_pct: number;
    best_spread_pct: number;
    avg_confidence: number;
    avg_quality_score: number;
  }>("/stats", {
    markets_scanned: 0,
    platforms_count: 0,
    platform_names: [],
    matched_pairs: 0,
    total_opportunities: 0,
    safe_opportunities: 0,
    caution_opportunities: 0,
    danger_opportunities: 0,
    avg_spread_pct: 0,
    best_spread_pct: 0,
    avg_confidence: 0,
    avg_quality_score: 0
  });
}

export async function fetchChainInfo() {
  return getJson<{
    bsc: { contract_address: string; explorer_url: string; verified: boolean; opportunity_count: number; network: string };
    opbnb: { contract_address: string; explorer_url: string; verified: boolean; opportunity_count: number; network: string };
    wallet_address: string;
    wallet_balance_bsc: string;
    wallet_balance_opbnb: string;
  }>("/chain-info", {
    bsc: { contract_address: "", explorer_url: "", verified: false, opportunity_count: 0, network: "" },
    opbnb: { contract_address: "", explorer_url: "", verified: false, opportunity_count: 0, network: "" },
    wallet_address: "",
    wallet_balance_bsc: "N/A",
    wallet_balance_opbnb: "N/A"
  });
}
