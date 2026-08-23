$ErrorActionPreference = "Stop"

$projectRoot = Split-Path $PSScriptRoot -Parent

Set-Location $projectRoot

Write-Host "Iniciando Telegram Bot..." -ForegroundColor Green

& "$projectRoot\.venv\Scripts\python.exe" -m app.bot.main