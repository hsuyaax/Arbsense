"""Send multiple reportOpportunity transactions to BSC Testnet using raw tx signing.

Bypasses .transact() POA middleware issue by using build_transaction + sign + send_raw.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from web3 import Web3

from src.config import load_settings

# --- Config ---
settings = load_settings()
RPC_URL = settings.bsc_testnet_rpc
PRIVATE_KEY = settings.private_key
CONTRACT_ADDRESS = settings.bsc_contract_address
CHAIN_ID = 97

# Load ABI
artifact_path = PROJECT_ROOT / "contracts" / "ArbSenseRegistry.artifact.json"
artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
ABI = artifact["abi"]

# Opportunities to report (from real data)
OPPORTUNITIES = [
    {
        "market_a": "pf-ct25-india",
        "market_b": "pr-icc-ct25-india",
        "spread_bps": 800,        # 8.0% spread
        "confidence_bps": 9500,    # 95% confidence
    },
    {
        "market_a": "be-eth-7k-2025",
        "market_b": "pf-eth-7000-2025",
        "spread_bps": 600,        # 6.0% spread
        "confidence_bps": 9500,    # 95% confidence
    },
    {
        "market_a": "pr-sol-etf-2025",
        "market_b": "xo-solana-etf-2025",
        "spread_bps": 700,        # 7.0% spread
        "confidence_bps": 9500,    # 95% confidence
    },
]


def main() -> None:
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("ERROR: Cannot connect to BSC Testnet RPC")
        sys.exit(1)

    chain_id = int(w3.eth.chain_id)
    print(f"Connected to chain_id={chain_id}")
    assert chain_id == CHAIN_ID, f"Expected chain {CHAIN_ID}, got {chain_id}"

    account = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"Wallet: {account.address}")

    balance = w3.eth.get_balance(account.address)
    print(f"Balance: {w3.from_wei(balance, 'ether')} tBNB")

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=ABI,
    )

    # Check current count
    count_before = contract.functions.getOpportunityCount().call()
    print(f"On-chain opportunities before: {count_before}")

    nonce = w3.eth.get_transaction_count(account.address)
    tx_hashes = []

    for i, opp in enumerate(OPPORTUNITIES):
        print(f"\n--- Transaction {i + 1}/{len(OPPORTUNITIES)} ---")
        print(f"  Market A: {opp['market_a']}")
        print(f"  Market B: {opp['market_b']}")
        print(f"  Spread:   {opp['spread_bps']} bps")
        print(f"  Confidence: {opp['confidence_bps']} bps")

        tx = contract.functions.reportOpportunity(
            opp["market_a"],
            opp["market_b"],
            opp["spread_bps"],
            opp["confidence_bps"],
        ).build_transaction({
            "from": account.address,
            "nonce": nonce + i,
            "chainId": CHAIN_ID,
            "gas": 500_000,
            "gasPrice": w3.eth.gas_price,
        })

        signed = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"  Tx sent: {tx_hash.hex()}")

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        print(f"  Status: {'SUCCESS' if receipt.status == 1 else 'FAILED'}")
        print(f"  Block: {receipt.blockNumber}")
        print(f"  Gas used: {receipt.gasUsed}")
        print(f"  Explorer: https://testnet.bscscan.com/tx/0x{tx_hash.hex()}")
        tx_hashes.append(tx_hash.hex())

        if i < len(OPPORTUNITIES) - 1:
            time.sleep(2)

    # Verify
    count_after = contract.functions.getOpportunityCount().call()
    print(f"\n=== SUMMARY ===")
    print(f"Opportunities before: {count_before}")
    print(f"Opportunities after:  {count_after}")
    print(f"Transactions sent:    {len(tx_hashes)}")
    for j, h in enumerate(tx_hashes):
        print(f"  Tx {j+1}: https://testnet.bscscan.com/tx/0x{h}")


if __name__ == "__main__":
    main()
