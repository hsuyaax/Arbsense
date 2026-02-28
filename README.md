# ArbSense

**AI-Powered Prediction Market Intelligence on BNB Chain**

ArbSense aggregates prediction markets from 7 platforms, uses OpenAI embeddings and Claude AI to detect semantically equivalent markets, identifies safe arbitrage opportunities after fees and slippage, and reports verified opportunities on-chain.

## Live Deployment

- **Network:** BSC Testnet (Chain ID 97)
- **Contract:** [`0x7Ba8FA52dAEd1c1Ea1acEB26E52339946458DeDa`](https://testnet.bscscan.com/address/0x7Ba8FA52dAEd1c1Ea1acEB26E52339946458DeDa)
- **Status:** Verified on BscScan

## How It Works

```
COLLECT (7 APIs) → EMBED (OpenAI) → MATCH (Cosine) → VERIFY (Claude) → DETECT (Economics) → REPORT (BSC)
```

1. **Collect** — Aggregates 100+ markets from Polymarket, Kalshi, predict.fun, Probable, XO Market, Opinion, Bento
2. **Embed** — Converts markets to 1536-dim semantic vectors via OpenAI
3. **Match** — Cross-platform cosine similarity (threshold: 0.70)
4. **Verify** — Claude Sonnet 4 analyzes resolution criteria alignment (triple fallback: Claude → GPT-4o-mini → local)
5. **Detect** — Calculates net profit after 1% fees, 0.5% slippage, gas costs
6. **Report** — Publishes verified opportunities to ArbSenseRegistry on BSC Testnet

## Quick Start

```bash
# Backend
pip install -r requirements.txt
cp .env.example .env   # Add your API keys

# Run pipeline
python scripts/run_agent.py --use-live

# Start API
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm install && npm run dev
```

Open `http://localhost:3000`

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, Tailwind CSS, Three.js |
| API | FastAPI, SSE streaming |
| AI | OpenAI embeddings, Claude Sonnet 4, GPT-4o-mini |
| Blockchain | Solidity 0.8.19, web3.py, BSC Testnet |

## Project Structure

```
src/                    # Python pipeline
  agent.py              # Orchestrator
  data_collector.py     # Market aggregation
  embeddings.py         # Semantic embeddings
  semantic_matcher.py   # AI verification
  arbitrage_detector.py # Opportunity scoring
  blockchain.py         # Web3 integration
  connectors/           # Live API connectors
api/                    # FastAPI server
contracts/              # Solidity smart contract
frontend/               # Next.js dashboard
scripts/                # CLI entry points
```

## Environment Variables

```
OPENAI_API_KEY=         # Required for embeddings
ANTHROPIC_API_KEY=      # Required for verification
BSC_TESTNET_RPC=        # BNB Chain RPC
PRIVATE_KEY=            # Wallet for on-chain reporting
BSC_CONTRACT_ADDRESS=   # Deployed contract
```

---

Built for BNB Chain Hackathon 2026
