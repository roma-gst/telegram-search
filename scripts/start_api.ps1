$ErrorActionPreference = "Stop"

$projectRoot = Split-Path $PSScriptRoot -Parent

Set-Location $projectRoot

Write-Host "Iniciando FastAPI..." -ForegroundColor Green

& "$projectRoot\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload