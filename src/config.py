"""Centralized environment and runtime configuration for ArbSense."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal environments
    def load_dotenv() -> None:
        """No-op fallback when python-dotenv is unavailable."""
        return None


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    openai_api_key: str
    anthropic_api_key: str
    bsc_testnet_rpc: str
    opbnb_testnet_rpc: str
    private_key: str
    bsc_contract_address: str
    opbnb_contract_address: str
    min_liquidity_usd: float
    embedding_model: str
    verifier_model: str
    max_embedding_inputs_per_run: int
    max_verification_calls_per_run: int
    max_usd_budget_per_run: float
    data_dir: Path


def load_settings() -> Settings:
    """Load settings from `.env` with safe defaults where possible."""
    load_dotenv()

    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", "").strip(),
        bsc_testnet_rpc=os.getenv(
            "BSC_TESTNET_RPC", "https://data-seed-prebsc-1-s1.bnbchain.org:8545"
        ).strip(),
        opbnb_testnet_rpc=os.getenv(
            "OPBNB_TESTNET_RPC", "https://opbnb-testnet-rpc.bnbchain.org"
        ).strip(),
        private_key=os.getenv("PRIVATE_KEY", "").strip(),
        bsc_contract_address=os.getenv("BSC_CONTRACT_ADDRESS", "").strip(),
        opbnb_contract_address=os.getenv("OPBNB_CONTRACT_ADDRESS", "").strip(),
        min_liquidity_usd=float(os.getenv("MIN_LIQUIDITY_USD", "1000")),
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small").strip(),
        verifier_model=os.getenv("VERIFIER_MODEL", "claude-sonnet-4-20250514").strip(),
        max_embedding_inputs_per_run=int(os.getenv("MAX_EMBEDDING_INPUTS_PER_RUN", "200")),
        max_verification_calls_per_run=int(
            os.getenv("MAX_VERIFICATION_CALLS_PER_RUN", "120")
        ),
        max_usd_budget_per_run=float(os.getenv("MAX_USD_BUDGET_PER_RUN", "3.0")),
        data_dir=data_dir,
    )
