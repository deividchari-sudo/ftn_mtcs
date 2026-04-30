#!/usr/bin/env pwsh
# Iniciar Vite dev server

Set-Location $PSScriptRoot
npx vite --host 0.0.0.0 --port 3000
