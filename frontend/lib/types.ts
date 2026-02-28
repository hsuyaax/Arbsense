export type MarketOutcome = {
  name: string;
  price: number;
  liquidity: number;
};

export type Market = {
  platform: string;
  market_id: string;
  title: string;
  description: string;
  outcomes: MarketOutcome[];
  resolution_date: string;
  category: string;
  quality_score?: number;
  quality_grade?: string;
  quality_reasoning?: string;
};

export type Verification = {
  is_match: boolean;
  confidence: number;
  reasoning: string;
  event_summary: string;
  outcome_mapping: Array<Record<string, string>>;
  key_differences: string[];
  risk_factors: string[];
  arbitrage_safe: boolean;
  resolution_conflict_score?: number;
  resolution_verdict?: "SAFE" | "CAUTION" | "DANGER";
  resolution_analysis?: string;
};

export type MatchRow = {
  is_match: boolean;
  confidence: number;
  reasoning: string;
  market_a: Market;
  market_b: Market;
  platform_a: string;
  platform_b: string;
  embedding_similarity: number;
  resolution_conflict_score: number;
  safety_badge: "SAFE" | "CAUTION" | "DANGER";
  resolution_risks: string[];
  resolution_criteria_a: string;
  resolution_criteria_b: string;
  edge_cases: string[];
  outcome_mapping: Array<Record<string, string>> | Record<string, string>;
  event_summary: string;
};

export type OpportunityRow = {
  event_summary: string;
  market_a: {
    platform: string;
    title: string;
    yes_price: number;
    no_price: number;
    liquidity: number;
  };
  market_b: {
    platform: string;
    title: string;
    yes_price: number;
    no_price: number;
    liquidity: number;
  };
  spread_pct: number;
  score: number;
  action: string;
  ai_confidence: number;
  profit_pct: number;
  safety_badge: "SAFE" | "CAUTION" | "DANGER";
  resolution_conflict_score: number;
  reasoning: string;
  resolution_risks: string[];
  outcome_mapping: Array<Record<string, string>> | Record<string, string>;
  time_decay_flag: boolean;
};
