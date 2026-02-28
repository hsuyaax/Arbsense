# Contributing to ArbSense

## Development Principles

1. Keep API read-only. Private keys must never be used in FastAPI endpoints.
2. Blockchain writes must happen only via scripts/agent (`scripts/run_agent.py`, `scripts/report_opportunity.py`).
3. Preserve chain safety guardrails (`97` BSC testnet, `5611` opBNB testnet).
4. Prefer small, reviewable commits by module.

## Local Workflow

1. Activate environment:
```powershell
.\.venv\Scripts\Activate.ps1
```
2. Run one cycle:
```powershell
python scripts/run_agent.py
```
3. Run API:
```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
4. Run frontend:
```powershell
cd frontend
copy .env.local.example .env.local
npm install
npm run dev
```

## Code Expectations

1. Add docstrings for all new modules/functions.
2. Keep type hints on Python function signatures.
3. Avoid hardcoded secrets in code and docs.
4. Keep deterministic local fallbacks for demo resilience.

## Pull Request Checklist

1. `python -m py_compile` passes for changed Python files.
2. API endpoints still return valid JSON for `/stats`, `/matches`, `/opportunities`.
3. Frontend tabs render with empty-data fallback states.
4. `README.md` and `docs/` are updated if behavior changes.
