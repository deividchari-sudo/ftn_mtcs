#!/usr/bin/env pwsh
# Script para iniciar ambiente de desenvolvimento completo
# Frontend (React + Vite) + Backend (Python Dash/FastAPI)

param(
    [switch]$SkipBackend,
    [switch]$SkipFrontend,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Uso: .\start-dev.ps1 [opcoes]

Opcoes:
    -SkipBackend   : Nao inicia o backend Python
    -SkipFrontend  : Nao inicia o frontend React
    -Help          : Mostra esta ajuda

Exemplos:
    .\start-dev.ps1                    # Inicia ambos
    .\start-dev.ps1 -SkipFrontend      # Apenas backend
    .\start-dev.ps1 -SkipBackend       # Apenas frontend
"@
    exit 0
}

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║           🚀 INICIANDO AMBIENTE DE DESENVOLVIMENTO             ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Backend:  http://localhost:8050                               ║
║  Frontend: http://localhost:3000                               ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

$backendJob = $null
$frontendJob = $null

# Iniciar Backend Python
try {
    if (-not $SkipBackend) {
        Write-Host "🐍 Iniciando Backend Python..." -ForegroundColor Green
        $backendJob = Start-Job -ScriptBlock {
            Set-Location $using:PWD
            python app.py 2>&1
        }
        Write-Host "   Backend iniciado em background (Job ID: $($backendJob.Id))" -ForegroundColor Gray
    }
} catch {
    Write-Error "Falha ao iniciar backend: $_"
}

# Iniciar Frontend React
Start-Sleep -Seconds 2

try {
    if (-not $SkipFrontend) {
        Write-Host "⚛️  Iniciando Frontend React..." -ForegroundColor Blue
        $frontendJob = Start-Job -ScriptBlock {
            Set-Location "$using:PWD\frontend"
            npm run dev 2>&1
        }
        Write-Host "   Frontend iniciado em background (Job ID: $($frontendJob.Id))" -ForegroundColor Gray
    }
} catch {
    Write-Error "Falha ao iniciar frontend: $_"
}

# Aguardar e mostrar logs
Write-Host ""
Write-Host "⏳ Aguardando servicos iniciarem..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "📊 STATUS DOS SERVICOS:" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════"

if ($backendJob) {
    $backendStatus = Receive-Job -Job $backendJob -Keep | Select-Object -Last 5
    if ($backendStatus) {
        Write-Host "Backend logs:" -ForegroundColor Green
        $backendStatus | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    }
}

if ($frontendJob) {
    $frontendStatus = Receive-Job -Job $frontendJob -Keep | Select-Object -Last 5
    if ($frontendStatus) {
        Write-Host "Frontend logs:" -ForegroundColor Blue
        $frontendStatus | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    }
}

Write-Host ""
Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║                     ✅ SERVICOS ATIVOS                         ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  🌐 Acesse: http://localhost:3000                               ║
║                                                                ║
║  Para parar: Ctrl+C ou feche esta janela                      ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Green

# Manter script rodando e mostrar logs em tempo real
try {
    while ($true) {
        Start-Sleep -Seconds 2
        
        if ($backendJob -and $backendJob.State -eq 'Running') {
            $logs = Receive-Job -Job $backendJob
            if ($logs) { $logs | ForEach-Object { Write-Host "[BACKEND] $_" -ForegroundColor DarkGreen } }
        }
        
        if ($frontendJob -and $frontendJob.State -eq 'Running') {
            $logs = Receive-Job -Job $frontendJob
            if ($logs) { $logs | ForEach-Object { Write-Host "[FRONTEND] $_" -ForegroundColor DarkBlue } }
        }
    }
} finally {
    # Cleanup ao sair
    Write-Host "`n🛑 Parando servicos..." -ForegroundColor Yellow
    if ($backendJob) { Stop-Job -Job $backendJob -ErrorAction SilentlyContinue; Remove-Job -Job $backendJob -ErrorAction SilentlyContinue }
    if ($frontendJob) { Stop-Job -Job $frontendJob -ErrorAction SilentlyContinue; Remove-Job -Job $frontendJob -ErrorAction SilentlyContinue }
    Write-Host "✅ Servicos parados" -ForegroundColor Green
}
