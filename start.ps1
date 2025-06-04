# start_monero.ps1

$moneroPath = "D:\MoneroCLI"                  # Where monerod.exe is located
$blockchainPath = "D:\MoneroBlockchain"       # New blockchain location (must contain lmdb)

# Navigate to monero directory
Set-Location $moneroPath

# Run monerod with external blockchain location
Start-Process -NoNewWindow -FilePath ".\monerod.exe" -ArgumentList "--data-dir `"$blockchainPath`""
Write-Host "monerod launched using blockchain data at $blockchainPath"
