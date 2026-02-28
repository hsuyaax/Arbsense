# Dependencies & Credits

## Python Backend

| Package | License | Purpose |
|---------|---------|---------|
| [FastAPI](https://github.com/tiangolo/fastapi) | MIT | REST API framework |
| [Uvicorn](https://github.com/encode/uvicorn) | BSD-3 | ASGI server |
| [web3.py](https://github.com/ethereum/web3.py) | MIT | Ethereum/BNB Chain interaction |
| [eth-account](https://github.com/ethereum/eth-account) | MIT | Transaction signing |
| [OpenAI Python SDK](https://github.com/openai/openai-python) | Apache-2.0 | Embeddings API client |
| [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) | MIT | Claude AI verification |
| [NumPy](https://github.com/numpy/numpy) | BSD-3 | Vector math / cosine similarity |
| [Pandas](https://github.com/pandas-dev/pandas) | BSD-3 | Data processing |
| [Requests](https://github.com/psf/requests) | Apache-2.0 | HTTP client for Polymarket/Kalshi |
| [py-solc-x](https://github.com/iamdefinitelyahuman/py-solc-x) | MIT | Solidity compiler |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | BSD-3 | Environment variable loading |

## Frontend

| Package | License | Purpose |
|---------|---------|---------|
| [Next.js](https://github.com/vercel/next.js) | MIT | React framework (SSR + App Router) |
| [React](https://github.com/facebook/react) | MIT | UI library |
| [Tailwind CSS](https://github.com/tailwindlabs/tailwindcss) | MIT | Utility-first CSS framework |
| [Three.js](https://github.com/mrdoob/three.js) | MIT | 3D animated background |
| [@react-three/fiber](https://github.com/pmndrs/react-three-fiber) | MIT | React Three.js integration |
| [@react-three/drei](https://github.com/pmndrs/drei) | MIT | Three.js helpers |
| [TypeScript](https://github.com/microsoft/TypeScript) | Apache-2.0 | Type safety |

## Blockchain

| Technology | License | Purpose |
|-----------|---------|---------|
| [Solidity](https://github.com/ethereum/solidity) | GPL-3.0 | Smart contract language |
| [BNB Smart Chain](https://github.com/bnb-chain/bsc) | LGPL-3.0 | Deployment network |

## External APIs

| API | Provider | Purpose |
|-----|----------|---------|
| [Polymarket Gamma API](https://gamma-api.polymarket.com) | Polymarket | Live prediction market data |
| [Kalshi Trade API](https://api.elections.kalshi.com) | Kalshi | Live prediction market data |
| [OpenAI Embeddings](https://platform.openai.com) | OpenAI | text-embedding-3-small vectors |
| [Claude API](https://api.anthropic.com) | Anthropic | Semantic match verification |
| [BSC Testnet RPC](https://data-seed-prebsc-1-s1.bnbchain.org:8545) | BNB Chain | Blockchain interaction |

## AI Models Used

| Model | Provider | Usage |
|-------|----------|-------|
| text-embedding-3-small | OpenAI | Market semantic embeddings (1536-dim) |
| Claude Sonnet 4 | Anthropic | Primary match verification |
| GPT-4o-mini | OpenAI | Secondary verification fallback |
