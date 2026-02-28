param(
  [switch]$RunAgentCycle = $true
)

$ErrorActionPreference = "Stop"
$root = "C:\Users\evenbeforebigbang\Desktop\arbsense"
$frontend = Join-Path $root "frontend"

Write-Host "ArbSense dev launcher starting..." -ForegroundColor Cyan

if ($RunAgentCycle) {
  Write-Host "Running one agent cycle..." -ForegroundColor Yellow
  & "$root\.venv\Scripts\python.exe" "$root\scripts\run_agent.py"
}

Write-Host "Starting FastAPI on :8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$root'; .\.venv\Scripts\Activate.ps1; uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
)

Write-Host "Starting Next.js frontend on :3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$frontend'; if (!(Test-Path .env.local)) { Copy-Item .env.local.example .env.local }; npm install; npm run dev"
)

Write-Host "Launched. Open http://localhost:3000" -ForegroundColor Cyan
