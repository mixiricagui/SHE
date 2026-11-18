$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:OLLAMA_NO_CLOUD = '1'
$env:OLLAMA_HOST = '127.0.0.1:11434'
$env:OLLAMA_NUM_PARALLEL = '1'
try {
    $null = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/version' -TimeoutSec 3
} catch {
    $leitor = Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'
    if (Test-Path -LiteralPath $leitor) {
        Start-Process -FilePath $leitor -ArgumentList 'serve' -WindowStyle Hidden
    } else {
        Write-Warning 'Ollama não encontrado. A tabela manual continua disponível.'
    }
}
& "$PSScriptRoot\.venv\Scripts\python.exe" -m streamlit run main.py
