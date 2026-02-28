"""Pydantic schemas aligned to ARBSENSE final document API design."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"


class MarketResponse(BaseModel):
    platform: str = ""
    market_id: str = ""
    title: str = ""
    description: str = ""
    outcomes: list[dict[str, Any]] = Field(default_factory=list)
    resolution_date: str = ""
    category: str = ""
    quality_score: int = 0
    quality_grade: str = "F"
    quality_reasoning: str = ""


class OpportunityResponse(BaseModel):
    market_a: dict[str, Any] = Field(default_factory=dict)
    market_b: dict[str, Any] = Field(default_factory=dict)
    spread_pct: float = 0.0
    profit_pct: float = 0.0
    action: str = ""
    safety_badge: str = "CAUTION"
    resolution_conflict_score: int = 50
    ai_confidence: float = 0.0
    score: float = 0.0
    reasoning: str = ""
    resolution_risks: list[str] = Field(default_factory=list)
    outcome_mapping: Any = Field(default_factory=dict)
    time_decay_flag: bool = False
    event_summary: str = ""


class MatchResponse(BaseModel):
    is_match: bool = False
    confidence: float = 0.0
    reasoning: str = ""
    market_a: dict[str, Any] = Field(default_factory=dict)
    market_b: dict[str, Any] = Field(default_factory=dict)
    platform_a: str = ""
    platform_b: str = ""
    embedding_similarity: float = 0.0
    resolution_conflict_score: int = 50
    safety_badge: str = "CAUTION"
    resolution_risks: list[str] = Field(default_factory=list)
    resolution_criteria_a: str = ""
    resolution_criteria_b: str = ""
    edge_cases: list[str] = Field(default_factory=list)
    outcome_mapping: Any = Field(default_factory=dict)
    event_summary: str = ""


class LogEntryResponse(BaseModel):
    timestamp: str = ""
    type: str = "system"
    message: str = ""
    cycle: int = 0


class StatsResponse(BaseModel):
    markets_scanned: int = 0
    platforms_count: int = 0
    platform_names: list[str] = Field(default_factory=list)
    matched_pairs: int = 0
    total_opportunities: int = 0
    safe_opportunities: int = 0
    caution_opportunities: int = 0
    danger_opportunities: int = 0
    avg_spread_pct: float = 0.0
    best_spread_pct: float = 0.0
    avg_confidence: float = 0.0
    avg_quality_score: float = 0.0


class ChainNetworkInfo(BaseModel):
    contract_address: str = ""
    explorer_url: str = ""
    verified: bool = False
    opportunity_count: int = 0
    network: str = ""


class ChainInfoResponse(BaseModel):
    bsc: ChainNetworkInfo = Field(default_factory=ChainNetworkInfo)
    opbnb: ChainNetworkInfo = Field(default_factory=ChainNetworkInfo)
    wallet_address: str = ""
    wallet_balance_bsc: str = "N/A"
    wallet_balance_opbnb: str = "N/A"
