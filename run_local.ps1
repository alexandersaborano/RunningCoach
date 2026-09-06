$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$venv = Join-Path $root ".venv"
$python = Join-Path $venv "Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "A criar ambiente virtual..."
    python -m venv $venv
}

& $python -m pip install -r (Join-Path $root "requirements.txt")

$envFile = Join-Path $root ".env"
$envExample = Join-Path $root ".env.example"
if (-not (Test-Path $envFile)) {
    Copy-Item $envExample $envFile
    Write-Host "Criado .env a partir de .env.example. Preenche as chaves se necessário."
}

Push-Location $root
try {
    & $python -m streamlit run ui/app.py
}
finally {
    Pop-Location
}
