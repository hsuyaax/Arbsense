"""Web3 integration helpers for ArbSense on BSC/opBNB testnets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config import Settings


ALLOWED_CHAIN_IDS = {97, 5611}
BSC_TESTNET_CHAIN_ID = 97
OPBNB_TESTNET_CHAIN_ID = 5611


def _require_web3() -> tuple[Any, Any, Any]:
    """Import web3 lazily so the codebase can run without web3 during bootstrap."""
    try:
        from web3 import Web3  # type: ignore
        from web3.middleware import SignAndSendRawMiddlewareBuilder  # type: ignore
        from web3.middleware import ExtraDataToPOAMiddleware  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise RuntimeError(
            "web3 is not installed. Install requirements before blockchain operations."
        ) from exc
    return Web3, SignAndSendRawMiddlewareBuilder, ExtraDataToPOAMiddleware


@dataclass
class NetworkConfig:
    """Network config for one deployment target."""

    name: str
    rpc_url: str
    contract_address: str


def load_contract_artifact(artifact_path: Path) -> dict[str, Any]:
    """Load compiled contract artifact JSON containing ABI/bytecode."""
    return json.loads(artifact_path.read_text(encoding="utf-8"))


class ArbSenseChainClient:
    """Chain client with strict testnet-only transaction guardrails."""

    def __init__(self, settings: Settings, network: str, abi: list[dict[str, Any]]):
        self.settings = settings
        self.network = network
        self.abi = abi

        self.net_cfg = self._resolve_network(network, settings)
        self.Web3, self.SignAndSendRawMiddlewareBuilder, self.ExtraDataToPOAMiddleware = _require_web3()
        self.w3 = self.Web3(self.Web3.HTTPProvider(self.net_cfg.rpc_url))
        if not self.w3.is_connected():
            raise RuntimeError(f"Unable to connect to {network} RPC: {self.net_cfg.rpc_url}")

        # BSC/opBNB are POA chains - inject middleware to handle extraData field
        self.w3.middleware_onion.inject(self.ExtraDataToPOAMiddleware, layer=0)

        self.chain_id = int(self.w3.eth.chain_id)
        if self.chain_id not in ALLOWED_CHAIN_IDS:
            raise RuntimeError(
                f"Refusing to transact on chain_id={self.chain_id}. "
                f"Allowed testnets: {sorted(ALLOWED_CHAIN_IDS)}"
            )

        self.account = self.w3.eth.account.from_key(self.settings.private_key)
        if not self.net_cfg.contract_address:
            raise RuntimeError(f"Missing contract address for network: {network}")
        self.contract = self.w3.eth.contract(
            address=self.Web3.to_checksum_address(self.net_cfg.contract_address),
            abi=self.abi,
        )

    @staticmethod
    def _resolve_network(network: str, settings: Settings) -> NetworkConfig:
        """Map network name to RPC and contract env vars."""
        normalized = network.strip().lower()
        if normalized == "bsc":
            return NetworkConfig(
                name="bsc",
                rpc_url=settings.bsc_testnet_rpc,
                contract_address=settings.bsc_contract_address,
            )
        if normalized == "opbnb":
            return NetworkConfig(
                name="opbnb",
                rpc_url=settings.opbnb_testnet_rpc,
                contract_address=settings.opbnb_contract_address,
            )
        raise ValueError(f"Unsupported network: {network}. Use 'bsc' or 'opbnb'.")

    def _apply_signing_middleware(self) -> None:
        """Attach local signing middleware for send_transaction flow."""
        middleware = self.SignAndSendRawMiddlewareBuilder.build(self.account)
        self.w3.middleware_onion.inject(middleware, layer=0)
        self.w3.eth.default_account = self.account.address

    def report_opportunity(
        self, market_a: str, market_b: str, spread_bps: int, confidence_bps: int
    ) -> str:
        """Send `reportOpportunity` transaction and return tx hash."""
        if self.chain_id not in ALLOWED_CHAIN_IDS:
            raise RuntimeError(
                f"Transaction blocked. chain_id={self.chain_id} not in allowed set."
            )
        self._apply_signing_middleware()

        tx_hash = self.contract.functions.reportOpportunity(
            market_a, market_b, int(spread_bps), int(confidence_bps)
        ).transact({"from": self.account.address})
        return tx_hash.hex()

    def get_opportunity_count(self) -> int:
        """Read total number of reported opportunities from chain."""
        return int(self.contract.functions.getOpportunityCount().call())

    def get_opportunity(self, index: int) -> dict[str, Any]:
        """Read one opportunity from chain."""
        row = self.contract.functions.getOpportunity(int(index)).call()
        return {
            "market_a": row[0],
            "market_b": row[1],
            "spread_bps": int(row[2]),
            "confidence_bps": int(row[3]),
            "timestamp": int(row[4]),
            "reporter": row[5],
        }
