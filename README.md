# ArbSense

ArbSense is a prediction market intelligence layer on BNB Chain: it aggregates markets, semantically matches equivalent events, scores resolution risk, and surfaces only safe arbitrage opportunities.

## Core Idea

Most arbitrage tools compare prices only. ArbSense compares prices **and** resolution criteria.

- Semantic matching finds equivalent markets across platforms.
- Resolution Risk Engine detects fine-print traps.
- Time-decay awareness avoids false arbitrage when deadlines differ.
- Safe opportunities are ranked and can be reported on-chain.

## Architecture

- Frontend: Next.js 14+ App Router + Tailwind (`frontend/`)
- API: FastAPI read-only backend (`api/main.py`)
- Intelligence: Python pipeline (`src/` + `scripts/`)
- Blockchain: Solidity + web3.py (`contracts/`, `src/blockchain.py`)

See:
- `docs/architecture.md`
- `docs/user-journey.md`
- `docs/business-model.md`

## Project Structure

```text
arbsense/
|-- api/
|   \-- main.py
|-- frontend/
|   |-- app/
|   |-- components/
|   \-- lib/
|-- src/
|-- scripts/
|-- contracts/
|-- docs/
|-- data/
|-- Dockerfile.api
|-- Dockerfile.frontend
\-- docker-compose.yml
```

## Setup (Windows)

```powershell
cd C:\Users\evenbeforebigbang\Desktop\arbsense
python -m virtualenv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create env file:

```powershell
Copy-Item .env.example .env
```

## Run Pipeline

```powershell
python scripts/collect_data.py --target-count 30
python scripts/generate_embeddings.py --threshold 0.70
python scripts/verify_matches.py --match-threshold 0.78
python scripts/detect_arbitrage.py
```

## Run Agent

Single cycle:

```powershell
python scripts/run_agent.py
```

Continuous:

```powershell
python scripts/run_agent.py --continuous --interval-seconds 300
```

Optional on-chain reporting:

```powershell
python scripts/run_agent.py --report-on-chain --network bsc
python scripts/run_agent.py --report-on-chain --network opbnb
```

## Run API + Frontend Locally

Terminal 1:

```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2:

```powershell
cd frontend
copy .env.local.example .env.local
npm install
npm run dev
```

Open:
- Frontend: `http://localhost:3000`
- API: `http://localhost:8000`

One-command dev launcher (opens two terminals):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev_up.ps1
```

## Docker (Both Services)

```powershell
docker compose up --build
```

Open:
- Frontend: `http://localhost:3000`
- API: `http://localhost:8000`

## API Endpoints

- `GET /health`
- `GET /markets`
- `GET /opportunities`
- `GET /matches`
- `GET /logs`
- `GET /stats`
- `GET /chain-info`

## Safety Logic

- Resolution verdict thresholds:
  - `SAFE < 30`
  - `CAUTION 30-70`
  - `DANGER > 70`
- Time-decay rule:
  - if resolution-date gap `> 7` days, classify as `time-value spread` and exclude from safe arb list.
- Chain safety:
  - transactions allowed only on chain IDs `97` (BSC testnet) and `5611` (opBNB testnet).

## Smart Contract Deployment

Recommended: Remix deploy + immediate BscScan verification.

Python option:

```powershell
python scripts/deploy_contract.py --network bsc
python scripts/deploy_contract.py --network opbnb
```

Then update `.env`:
- `BSC_CONTRACT_ADDRESS=...`
- `OPBNB_CONTRACT_ADDRESS=...`

## Dependencies

`requirements.txt` includes:
- web3
- eth-account
- python-dotenv
- openai
- anthropic
- numpy
- pandas
- requests
- py-solc-x
- fastapi
- uvicorn

Frontend dependencies are in `frontend/package.json`.

## Live Demo Checklist

1. Run one fresh cycle:
```powershell
python scripts/run_agent.py
```
2. Start API:
```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
3. Start frontend:
```powershell
cd frontend
copy .env.local.example .env.local
npm install
npm run dev
```
4. Open `http://localhost:3000`.
5. Demo flow:
   - Aggregator
   - Safe Opportunities
   - Resolution Risks (wow tab)
   - AI Analysis
   - Agent Feed
   - On-Chain

## License

MIT (`LICENSE`)
