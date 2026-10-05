param(
    [string]$ModelUrl = "https://huggingface.co/Qwen/Qwen3-8B-GGUF/resolve/main/Qwen3-8B-Q4_K_M.gguf?download=true",
    [string]$LlamaRelease = "v0.6.0"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$RuntimeDir = Join-Path $RepoRoot "runtime\llama\windows"
$ModelsDir = Join-Path $RepoRoot "models"
$TempDir = Join-Path $env:TEMP "lirico-ai-setup"

New-Item -ItemType Directory -Force -Path $RuntimeDir, $ModelsDir, $TempDir | Out-Null

Write-Host "Preparando motor local do Lirico AI..."

$releaseApi = "https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/$LlamaRelease"
$release = Invoke-RestMethod -Uri $releaseApi -Headers @{ "User-Agent" = "LiricoAI" }

$asset = $release.assets | Where-Object {
    $_.name -match "win.*x64.*\.zip$" -and $_.name -notmatch "cuda"
} | Select-Object -First 1

if (-not $asset) {
    throw "Nao foi encontrado pacote Windows x64 do llama.cpp na release $LlamaRelease."
}

$zipPath = Join-Path $TempDir $asset.name
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zipPath
Expand-Archive -Path $zipPath -DestinationPath $TempDir -Force

$server = Get-ChildItem -Path $TempDir -Recurse -Filter "llama-server.exe" | Select-Object -First 1
if (-not $server) {
    throw "llama-server.exe nao foi encontrado no pacote baixado."
}

Copy-Item $server.FullName (Join-Path $RuntimeDir "llama-server.exe") -Force

# Copia DLLs vizinhas necessárias para o mesmo diretório do runtime.
Get-ChildItem -Path $server.Directory.FullName -Filter "*.dll" | ForEach-Object {
    Copy-Item $_.FullName $RuntimeDir -Force
}

$modelPath = Join-Path $ModelsDir "lirico-default.gguf"
if (-not (Test-Path $modelPath)) {
    Write-Host "Baixando modelo Lirico AI Standard 8B..."
    Invoke-WebRequest -Uri $ModelUrl -OutFile $modelPath
}

Write-Host ""
Write-Host "Instalacao local concluida."
Write-Host "Runtime: $(Join-Path $RuntimeDir 'llama-server.exe')"
Write-Host "Modelo: $modelPath"
