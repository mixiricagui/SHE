$ErrorActionPreference = 'Stop'
$env:OLLAMA_NO_CLOUD = '1'
$env:OLLAMA_HOST = '127.0.0.1:11434'
$env:OLLAMA_NUM_PARALLEL = '1'
$comando = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $comando) { throw 'Instale o Ollama pelo site oficial e abra um novo PowerShell. Veja docs/LEITURA_LOCAL.md.' }
Write-Output 'Iniciando leitor somente local. Se a porta estiver ocupada, encerre o Ollama da bandeja antes de executar este script.'
& $comando.Source serve
