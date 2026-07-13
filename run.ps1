$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "A criar o ambiente virtual .venv..."

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        & $python.Source -m venv .venv
    }
    else {
        $py = Get-Command py -ErrorAction SilentlyContinue
        if (-not $py) {
            throw "Python 3 nao foi encontrado. Instale-o e execute novamente este script."
        }

        & $py.Source -3 -m venv .venv
    }
}

Write-Host "A instalar/verificar as dependencias..."
& $venvPython -m pip install -r requirements.txt

Write-Host "A iniciar o pre-processador..."
& $venvPython main.py
