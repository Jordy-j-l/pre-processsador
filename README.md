# Pré-processador FEM

Desenvolvimento de uma malha iterativa de elementos finitos tetraédicos.

## Requisitos

- Windows 10 ou 11
- Python 3 instalado e disponível no terminal
- Ligação à internet na primeira execução

## Executar

Depois de clonar o repositório, abra a pasta e faça duplo clique em:

```text
run.bat
```

Também pode iniciar pelo PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

O script cria automaticamente o ambiente virtual `.venv`, instala ou verifica as
dependências de `requirements.txt` e inicia a aplicação.

Nas execuções seguintes pode usar o mesmo comando. O ambiente virtual existente
será reutilizado.
