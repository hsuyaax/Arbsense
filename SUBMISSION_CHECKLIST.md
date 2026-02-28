# ArbSense Submission Checklist

## Product Readiness

- [ ] Run one fresh cycle: `python scripts/run_agent.py`
- [ ] Frontend loads on `http://localhost:3000`
- [ ] API loads on `http://localhost:8000/health`
- [ ] 6 tabs render correctly:
  - [ ] Aggregator
  - [ ] Safe Opportunities
  - [ ] Resolution Risks
  - [ ] AI Analysis
  - [ ] Agent Feed
  - [ ] On-Chain

## Required Artifacts

- [ ] Public GitHub repo
- [ ] `README.md` complete
- [ ] `LICENSE` present (MIT)
- [ ] `.env.example` has no real secrets
- [ ] `docs/architecture.md` with Mermaid
- [ ] `docs/user-journey.md` with Mermaid
- [ ] `docs/business-model.md`
- [ ] `docker-compose.yml`
- [ ] `Dockerfile.api`
- [ ] `Dockerfile.frontend`

## Blockchain Proof

- [ ] Contract deployed on BSC testnet
- [ ] Contract deployed on opBNB testnet
- [ ] BSC source verified on BscScan
- [ ] 2+ successful transactions recorded
- [ ] `.env` updated with:
  - [ ] `BSC_CONTRACT_ADDRESS`
  - [ ] `OPBNB_CONTRACT_ADDRESS`

## Demo Prep

- [ ] Backup demo video recorded (<= 3 minutes)
- [ ] Pitch deck ready
- [ ] Resolution Risks tab rehearsed as wow moment
- [ ] Tweet posted with `@BNBChain` and `#BNBHack`

## Last Sanity Check

- [ ] No secret keys committed
- [ ] No crash on empty-data states
- [ ] Agent logs visible in Agent Feed
- [ ] On-Chain tab links open correctly
