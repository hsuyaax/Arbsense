# User Journey

## 1. Core User Flow — Arbitrage Discovery

```mermaid
flowchart TD
    A[User opens ArbSense dashboard] --> B[Dashboard loads with SSR data]
    B --> C[SSE stream connects — live stats]
    C --> D{User browses tabs}

    D -->|Aggregator| E[Browse 100+ markets across 7 platforms]
    E --> E1[Filter by category / quality grade]
    E1 --> E2[Compare prices across platforms]

    D -->|Opportunities| F[View AI-scored arbitrage opportunities]
    F --> F1[See spread %, net profit, fees]
    F1 --> F2[Review recommended action]
    F2 --> F3[Click to view on BscScan]

    D -->|Risks| G[Side-by-side resolution comparison]
    G --> G1[Review conflict score 0-100]
    G1 --> G2[Check SAFE / CAUTION / DANGER badge]
    G2 --> G3[Read AI resolution analysis]

    D -->|Verification| H[See all AI match results]
    H --> H1[Accepted pairs with confidence]
    H --> H2[Rejected pairs with reasoning]

    D -->|Agent Feed| I[Real-time pipeline logs]

    D -->|Infrastructure| J[Contract address + wallet info]
    J --> J1[View on-chain reports on BscScan]

    D -->|Bets| K[Connect MetaMask wallet]
    K --> K1{Choose bet type}
    K1 -->|Habit| K2[Stake tBNB on personal goals]
    K1 -->|Fun| K3[Bet on social events]
    K1 -->|Custom| K4[Create your own bet]
    K2 --> K5[Confirm tx in MetaMask]
    K3 --> K5
    K4 --> K5
    K5 --> K6[TX hash displayed with BscScan link]

    C --> L[User clicks Refresh Live Data]
    L --> M[POST /refresh triggers pipeline]
    M --> N[New data flows via SSE]
    N --> C
```

## 2. Intelligence Pipeline Flow

```mermaid
flowchart LR
    subgraph Collection
        PA[Polymarket API] --> COLLECT
        KA[Kalshi API] --> COLLECT
        PF[predict.fun] --> COLLECT
        PR[Probable] --> COLLECT
        XO[XO Market] --> COLLECT
        OP[Opinion] --> COLLECT
        BE[Bento] --> COLLECT
    end

    COLLECT[Collect & Normalize] --> QS[Quality Score A-F]
    QS --> EMBED[OpenAI Embeddings]
    EMBED --> |1536-dim vectors| MATCH[Cosine Similarity]
    MATCH --> |threshold > 0.70| VERIFY

    subgraph AI Verification
        VERIFY[Claude Sonnet 4] --> |fallback| GPT[GPT-4o-mini]
        GPT --> |fallback| LOCAL[Local Deterministic]
    end

    VERIFY --> DETECT[Arbitrage Detection]
    DETECT --> |fees + slippage + gas| FILTER{Net profit > 0?}
    FILTER -->|Yes| SAFE[Safe Opportunities]
    FILTER -->|No| REJECT[Rejected]
    SAFE --> REPORT[Report On-Chain]
    REPORT --> BSC[(BSC Testnet)]
```

## 3. Wallet Connection Flow (Bets Tab)

```mermaid
sequenceDiagram
    actor User
    participant UI as ArbSense Dashboard
    participant MM as MetaMask
    participant BSC as BSC Testnet

    User->>UI: Click "Connect Wallet"
    UI->>MM: eth_requestAccounts
    MM->>User: Approve connection?
    User->>MM: Approve
    MM->>UI: Return address + chainId

    alt Wrong chain
        UI->>MM: wallet_switchEthereumChain (0x61)
        MM->>User: Switch to BSC Testnet?
        User->>MM: Approve
    end

    UI->>UI: Show wallet balance
    User->>UI: Select bet + amount
    User->>UI: Click "Place Bet"
    UI->>MM: eth_sendTransaction
    MM->>User: Confirm transaction?
    User->>MM: Confirm
    MM->>BSC: Broadcast transaction
    BSC->>MM: Return tx hash
    MM->>UI: Transaction confirmed
    UI->>User: Show tx hash + BscScan link
    UI->>UI: Refresh balance
```

## 4. Data Refresh Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (Next.js)
    participant API as FastAPI Server
    participant Pipeline as Python Agent
    participant AI as Claude / OpenAI
    participant Chain as BSC Testnet

    User->>FE: Click "Refresh Live Data"
    FE->>API: POST /refresh
    API->>Pipeline: Background task: run_live_pipeline()

    Pipeline->>Pipeline: Collect from 7 platforms
    Pipeline->>AI: Embed markets (OpenAI)
    AI-->>Pipeline: 1536-dim vectors
    Pipeline->>Pipeline: Find candidate pairs (cosine sim)
    Pipeline->>AI: Verify pairs (Claude)
    AI-->>Pipeline: Match results + verdicts
    Pipeline->>Pipeline: Detect opportunities
    Pipeline->>Chain: reportOpportunity() tx
    Chain-->>Pipeline: tx hash
    Pipeline->>Pipeline: Save all JSON files

    loop Every 5 seconds
        API->>API: Read JSON files
        API->>FE: SSE push stats
        FE->>User: Update dashboard metrics
    end
```

## 5. UX Improvements Over Existing Tools

| Existing Tool Pain Point | ArbSense Solution |
|--------------------------|-------------------|
| Manual platform-by-platform browsing | Single aggregated view of 7 platforms |
| No resolution criteria comparison | Side-by-side AI-powered risk analysis |
| Price-only arbitrage (misses traps) | Semantic matching + resolution verdict |
| No audit trail | Immutable on-chain proof on BSC |
| Static dashboards | Real-time SSE streaming + live refresh |
| No personal betting | Habit builder + fun bets with MetaMask |
| Complex interfaces | Clean monochrome UI with tab navigation |
