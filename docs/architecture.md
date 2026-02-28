# System Architecture

## High-Level Architecture

```mermaid
graph TB
    subgraph Frontend["Frontend (Next.js 15)"]
        UI[Dashboard UI]
        SSR[Server-Side Rendering]
        SSE_C[SSE Client Hook]
        WALLET[MetaMask Integration]
        TABS[7 Tab Components]
    end

    subgraph API["API Layer (FastAPI)"]
        REST[REST Endpoints x8]
        SSE_S[SSE Stream Generator]
        REFRESH[Refresh Trigger]
    end

    subgraph Pipeline["Intelligence Pipeline (Python)"]
        COLLECT[Data Collector]
        EMBED[Embedding Engine]
        MATCH[Candidate Matcher]
        VERIFY[AI Verifier]
        DETECT[Arbitrage Detector]
        QUALITY[Quality Scorer]
        REPORT[Chain Reporter]
    end

    subgraph External["External Data Sources"]
        POLY[Polymarket Gamma API]
        KALSHI[Kalshi Events API]
        BNB_P[BNB Chain Platforms x5]
    end

    subgraph AI["AI Services"]
        OPENAI[OpenAI text-embedding-3-small]
        CLAUDE[Claude Sonnet 4]
        GPT[GPT-4o-mini]
        LOCAL[Local Deterministic Fallback]
    end

    subgraph Blockchain["BNB Chain"]
        BSC[BSC Testnet]
        CONTRACT[ArbSenseRegistry.sol]
        OPBNB[opBNB Testnet]
    end

    subgraph Storage["Data Storage"]
        JSON[(JSON Files)]
        ENV[.env Config]
    end

    UI --> SSR --> REST
    SSE_C --> SSE_S
    UI --> WALLET --> BSC

    REST --> JSON
    REFRESH --> COLLECT
    SSE_S --> JSON

    COLLECT --> POLY
    COLLECT --> KALSHI
    COLLECT --> BNB_P
    COLLECT --> QUALITY --> EMBED
    EMBED --> OPENAI
    EMBED --> MATCH --> VERIFY
    VERIFY --> CLAUDE
    VERIFY --> GPT
    VERIFY --> LOCAL
    VERIFY --> DETECT --> REPORT
    REPORT --> CONTRACT
    CONTRACT --> BSC

    COLLECT --> JSON
    EMBED --> JSON
    MATCH --> JSON
    VERIFY --> JSON
    DETECT --> JSON
```

## Module Dependency Graph

```mermaid
graph LR
    config[config.py] --> agent[agent.py]
    config --> collector[data_collector.py]
    config --> embeddings[embeddings.py]
    config --> matcher[semantic_matcher.py]
    config --> blockchain[blockchain.py]

    collector --> agent
    collector --> polymarket[connectors/polymarket.py]
    collector --> kalshi[connectors/kalshi.py]
    collector --> quality[quality_scorer.py]

    embeddings --> agent
    matcher --> agent
    detector[arbitrage_detector.py] --> agent
    blockchain --> agent

    agent --> |writes| json[(data/*.json)]
    json --> api[api/main.py]
    api --> schemas[api/schemas.py]
```

## Smart Contract Architecture

```mermaid
classDiagram
    class ArbSenseRegistry {
        +Opportunity[] opportunities
        +reportOpportunity(marketA, marketB, spreadBps, confidenceBps)
        +getOpportunityCount() uint256
        +getOpportunity(index) Opportunity
        +event OpportunityReported
    }

    class Opportunity {
        +string marketA
        +string marketB
        +uint256 spreadBps
        +uint256 confidenceBps
        +uint256 timestamp
        +address reporter
    }

    ArbSenseRegistry "1" --> "*" Opportunity : stores
```

## Frontend Component Tree

```mermaid
graph TD
    PAGE[app/page.tsx SSR] --> SCENE[Scene Three.js BG]
    PAGE --> SHELL[DashboardShell]
    PAGE --> FOOTER[Footer]

    SHELL --> NAVBAR[Navbar]
    SHELL --> HEADER[Header]
    SHELL --> STATUS[Live Status Bar]
    SHELL --> METRICS[Metrics Bar x4]
    SHELL --> USP[USP Feature Strip x5]
    SHELL --> CONTENT{Active Tab}

    CONTENT --> AGG[AggregatorTab]
    CONTENT --> OPP[SafeOpportunitiesTab]
    CONTENT --> RISK[ResolutionRisksTab]
    CONTENT --> VER[AiAnalysisTab]
    CONTENT --> FEED[AgentFeedTab]
    CONTENT --> INFRA[OnChainTab]
    CONTENT --> BETS[FunBetsTab]

    BETS --> WALLET_UI[Wallet Connect]
    BETS --> HABIT[Habit Builder]
    BETS --> FUN[Fun Bets]
    BETS --> CUSTOM[Custom Bet Creator]
```

## AI Verification Pipeline Detail

```mermaid
flowchart TD
    INPUT[Candidate Pair] --> PROMPT[Build Verification Prompt]
    PROMPT --> CLAUDE_TRY{Claude Sonnet 4}

    CLAUDE_TRY -->|Success| PARSE[Parse JSON Response]
    CLAUDE_TRY -->|Fail| GPT_TRY{GPT-4o-mini}

    GPT_TRY -->|Success| PARSE
    GPT_TRY -->|Fail| LOCAL_TRY[Local Deterministic]

    LOCAL_TRY --> PARSE

    PARSE --> EXTRACT[Extract Fields]
    EXTRACT --> IS_MATCH{is_match?}

    IS_MATCH -->|true| CONFIDENCE{confidence >= 0.78?}
    IS_MATCH -->|false| REJECTED[Rejected Pair]

    CONFIDENCE -->|Yes| VERDICT{resolution_verdict}
    CONFIDENCE -->|No| REJECTED

    VERDICT -->|SAFE| SAFE_OPP[Safe for Arbitrage]
    VERDICT -->|CAUTION| CAUTION_OPP[Display with Warning]
    VERDICT -->|DANGER| BLOCKED[Blocked from Opportunities]

    SAFE_OPP --> ECONOMICS[Calculate Economics]
    ECONOMICS --> NET{net_profit > 0?}
    NET -->|Yes| OPPORTUNITY[Final Opportunity]
    NET -->|No| REJECTED
```

## Data Flow Diagram

```mermaid
flowchart LR
    subgraph Input
        M1[Polymarket Markets]
        M2[Kalshi Markets]
        M3[BNB Platform Markets]
    end

    subgraph Processing
        N[Normalized Markets<br>data/markets.json]
        E[Embeddings<br>data/embeddings.json]
        C[Candidate Pairs<br>data/candidate_pairs.json]
        V[Verified Matches<br>data/verified_matches.json]
        O[Opportunities<br>data/opportunities.json]
        L[Agent Logs<br>data/agent_logs.json]
    end

    subgraph Output
        API_OUT[FastAPI /markets<br>/opportunities<br>/matches<br>/stats]
        SSE_OUT[SSE /stream]
        CHAIN_OUT[BSC Testnet<br>On-chain Reports]
        DASH_OUT[Dashboard<br>7 Tabs]
    end

    M1 --> N
    M2 --> N
    M3 --> N
    N --> E --> C --> V --> O

    N --> L
    E --> L
    V --> L
    O --> L

    N --> API_OUT
    O --> API_OUT
    V --> API_OUT
    L --> API_OUT
    N --> SSE_OUT
    O --> CHAIN_OUT
    API_OUT --> DASH_OUT
    SSE_OUT --> DASH_OUT
```

## Network Architecture

```mermaid
graph LR
    subgraph Client
        BROWSER[Browser :3000]
    end

    subgraph Server
        NEXTJS[Next.js SSR :3000]
        FASTAPI[FastAPI :8000]
    end

    subgraph External
        OPENAI_API[OpenAI API]
        ANTHROPIC_API[Anthropic API]
        POLY_API[Polymarket API]
        KALSHI_API[Kalshi API]
        BSC_RPC[BSC Testnet RPC]
    end

    BROWSER -->|HTTP/SSE| NEXTJS
    NEXTJS -->|SSR fetch| FASTAPI
    BROWSER -->|SSE| FASTAPI
    BROWSER -->|MetaMask| BSC_RPC

    FASTAPI -->|Read| JSON[(data/*.json)]
    FASTAPI -->|Pipeline trigger| OPENAI_API
    FASTAPI -->|Pipeline trigger| ANTHROPIC_API
    FASTAPI -->|Pipeline trigger| POLY_API
    FASTAPI -->|Pipeline trigger| KALSHI_API
    FASTAPI -->|web3.py| BSC_RPC
```

## Deployment Architecture

```mermaid
graph TD
    subgraph Docker["Docker Compose"]
        API_C[api container<br>Dockerfile.api<br>Port 8000]
        FE_C[frontend container<br>Dockerfile.frontend<br>Port 3000]
    end

    subgraph Config
        ENV[.env]
        ENV_EX[.env.example]
    end

    ENV --> API_C
    API_C --> FE_C

    API_C --> BSC_NET[BSC Testnet :8545]
    API_C --> OPENAI_NET[OpenAI API]
    API_C --> ANTHRO_NET[Anthropic API]
```
