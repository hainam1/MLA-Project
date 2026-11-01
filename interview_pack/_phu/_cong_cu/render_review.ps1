$ErrorActionPreference = 'Stop'
$packRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$inputDoc = Join-Path $packRoot '15_review_tuan10_mau.docx'
$outputPdf = Join-Path $packRoot '_phu/_kiem_tra/toi_uu/15_review_word_render.pdf'
$wordInstance = New-Object -ComObject Word.Application
try {
    $wordInstance.Visible = $false
    $wordInstance.DisplayAlerts = 0
    $document = $wordInstance.Documents.Open($inputDoc, $false, $true)
    try { $document.ExportAsFixedFormat($outputPdf, 17) }
    finally { $document.Close(0) }
} finally { $wordInstance.Quit() }
Write-Output 'Rendered review DOCX with installed Word engine'
