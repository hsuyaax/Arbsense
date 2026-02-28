"""Compile and deploy ArbSenseRegistry contract using web3.py."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_settings


def _require_web3_and_solcx() -> tuple[Any, Any]:
    """Import web3 + solcx lazily for better bootstrap ergonomics."""
    try:
        from web3 import Web3  # type: ignore
        from solcx import compile_standard, install_solc  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Missing dependencies. Install web3 and py-solc-x before deployment."
        ) from exc
    return Web3, (compile_standard, install_solc)


def parse_args() -> argparse.Namespace:
    """Parse CLI args."""
    parser = argparse.ArgumentParser(description="Compile/deploy ArbSenseRegistry.")
    parser.add_argument("--network", choices=["bsc", "opbnb"], default="bsc")
    parser.add_argument(
        "--artifact-output",
        type=str,
        default="contracts/ArbSenseRegistry.artifact.json",
        help="Where to save ABI/bytecode artifact.",
    )
    parser.add_argument(
        "--solc-version", type=str, default="0.8.19", help="Solidity compiler version."
    )
    return parser.parse_args()


def main() -> None:
    """Compile and deploy the contract to selected testnet."""
    args = parse_args()
    settings = load_settings()
    Web3, solcx_fns = _require_web3_and_solcx()
    compile_standard, install_solc = solcx_fns

    network = args.network
    rpc_url = settings.bsc_testnet_rpc if network == "bsc" else settings.opbnb_testnet_rpc
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise RuntimeError(f"Failed to connect to RPC: {rpc_url}")

    chain_id = int(w3.eth.chain_id)
    if chain_id not in {97, 5611}:
        raise RuntimeError(f"Unsafe chain ID {chain_id}. Allowed only 97/5611.")

    contract_path = PROJECT_ROOT / "contracts" / "ArbSenseRegistry.sol"
    source_code = contract_path.read_text(encoding="utf-8")

    install_solc(args.solc_version)
    compiled = compile_standard(
        {
            "language": "Solidity",
            "sources": {"ArbSenseRegistry.sol": {"content": source_code}},
            "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}},
        },
        solc_version=args.solc_version,
    )

    contract_data = compiled["contracts"]["ArbSenseRegistry.sol"]["ArbSenseRegistry"]
    abi = contract_data["abi"]
    bytecode = contract_data["evm"]["bytecode"]["object"]
    artifact = {"abi": abi, "bytecode": bytecode, "solc_version": args.solc_version}
    artifact_path = Path(args.artifact_output)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    account = w3.eth.account.from_key(settings.private_key)
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    nonce = w3.eth.get_transaction_count(account.address)
    tx = contract.constructor().build_transaction(
        {
            "from": account.address,
            "nonce": nonce,
            "chainId": chain_id,
            "gas": 3_000_000,
            "gasPrice": w3.eth.gas_price,
        }
    )
    signed = w3.eth.account.sign_transaction(tx, private_key=settings.private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Network: {network} (chain_id={chain_id})")
    print(f"Contract deployed at: {receipt.contractAddress}")
    print(f"Deployment tx hash: {tx_hash.hex()}")
    print("Update your .env:")
    if network == "bsc":
        print(f"BSC_CONTRACT_ADDRESS={receipt.contractAddress}")
    else:
        print(f"OPBNB_CONTRACT_ADDRESS={receipt.contractAddress}")
    print("Then verify source in explorer immediately (recommended).")


if __name__ == "__main__":
    main()
