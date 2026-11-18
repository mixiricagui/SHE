param([Parameter(Mandatory=$true)][string]$Original)
$ErrorActionPreference = 'Stop'
$destino = Join-Path (Split-Path $PSScriptRoot) 'modelos\modelo_inspecao.xlsx'
if (Test-Path -LiteralPath $destino) { throw 'A cópia já existe; não será sobrescrita.' }
$excel = $null
$livro = $null
try {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    $excel.AutomationSecurity = 3
    $excel.AskToUpdateLinks = $false
    $livro = $excel.Workbooks.Open($Original, 0, $true)
    foreach ($aba in $livro.Worksheets) {
        Write-Output ("ABA {0}: {1}; impressão={2}" -f $aba.Name, $aba.UsedRange.Address(), $aba.PageSetup.PrintArea)
    }
    $livro.SaveAs($destino, 51)
    Write-Output 'Cópia XLSX criada. Original aberto somente para leitura; validação visual ainda necessária.'
} finally {
    if ($null -ne $livro) { $livro.Close($false); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($livro) }
    if ($null -ne $excel) { $excel.Quit(); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($excel) }
}
