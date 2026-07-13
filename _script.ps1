$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

function Test-PythonCommand {
    param(
        [string]$Command,
        [string[]]$Arguments = @()
    )

    try {
        & $Command @Arguments --version *> $null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

if (-not (Test-Path $venvPython)) {
    Write-Host "A criar o ambiente virtual .venv..."

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py -and (Test-PythonCommand -Command $py.Source -Arguments @("-3"))) {
        & $py.Source -3 -m venv .venv
    }
    else {
        $python = Get-Command python -ErrorAction SilentlyContinue
        if ($python -and (Test-PythonCommand -Command $python.Source)) {
            & $python.Source -m venv .venv
        }
        else {
            throw @"
Python 3 nao foi encontrado.

O comando 'python' encontrado pelo Windows e provavelmente um atalho quebrado da Microsoft Store.
Instale o Python 3 a partir de https://www.python.org/downloads/windows/
Durante a instalacao, selecione 'Add python.exe to PATH'.
Depois, volte a abrir run.bat.
"@
        }
    }
}

if (-not (Test-Path $venvPython)) {
    throw "O ambiente virtual nao foi criado corretamente. Apague a pasta .venv e tente novamente."
}

Write-Host "A instalar/verificar as dependencias..."
& $venvPython -m pip install -r requirements.txt

Write-Host "A iniciar o pre-processador..."
& $venvPython main.py
