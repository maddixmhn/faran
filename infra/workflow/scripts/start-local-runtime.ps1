$ErrorActionPreference = 'Stop'

$workflowDir = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$repoDir = [IO.Path]::GetFullPath((Join-Path $workflowDir '..\..'))
$dataDir = Join-Path $workflowDir 'data\paperclip-sandbox'
$logDir = Join-Path $workflowDir 'data\launcher-logs'
$logFile = Join-Path $logDir 'startup.log'
$dockerExe = 'C:\Program Files\Docker\Docker\Docker Desktop.exe'
$npxCmd = 'C:\Program Files\nodejs\npx.cmd'
$paperclipHealth = 'http://127.0.0.1:3100/api/health'

New-Item -ItemType Directory -Force -Path $logDir | Out-Null
function Write-RunLog([string]$Message) {
  Add-Content -LiteralPath $logFile -Value "$(Get-Date -Format o) $Message"
}

Write-RunLog 'Starting local workflow runtime check.'

if (-not (Get-Process -Name 'Docker Desktop' -ErrorAction SilentlyContinue)) {
  if (-not (Test-Path -LiteralPath $dockerExe)) { throw 'Docker Desktop executable was not found.' }
  Start-Process -FilePath $dockerExe -WindowStyle Hidden | Out-Null
  Write-RunLog 'Started Docker Desktop.'
}

$dockerReady = $false
for ($attempt = 0; $attempt -lt 36; $attempt++) {
  & docker info *> $null
  if ($LASTEXITCODE -eq 0) { $dockerReady = $true; break }
  Start-Sleep -Seconds 5
}
if (-not $dockerReady) { throw 'Docker Engine did not become ready within 180 seconds.' }

Push-Location $workflowDir
try {
  & docker compose --env-file .env -f compose.yaml -f compose.local.yaml up -d n8n n8n-db
  if ($LASTEXITCODE -ne 0) { throw 'Could not start the local n8n/PostgreSQL services.' }
} finally {
  Pop-Location
}
Write-RunLog 'Ensured n8n and PostgreSQL containers are running.'

$paperclipReady = $false
try {
  $null = Invoke-RestMethod -Uri $paperclipHealth -TimeoutSec 3
  $paperclipReady = $true
} catch { }

if (-not $paperclipReady) {
  $stdout = Join-Path $logDir 'paperclip.stdout.log'
  $stderr = Join-Path $logDir 'paperclip.stderr.log'
  $cachedCli = Get-ChildItem "$env:LOCALAPPDATA\npm-cache\_npx" -Directory -ErrorAction SilentlyContinue |
    ForEach-Object { Join-Path $_.FullName 'node_modules\paperclipai\dist\index.js' } |
    Where-Object { Test-Path -LiteralPath $_ } |
    Select-Object -First 1
  if ($cachedCli) {
    $nodeExe = (Get-Command node -ErrorAction Stop).Source
    $arguments = @($cachedCli, 'run', '--data-dir', $dataDir, '--bind', 'loopback', '--no-repair')
    Start-Process -FilePath $nodeExe -ArgumentList $arguments -WorkingDirectory $repoDir -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr | Out-Null
    Write-RunLog 'Started Paperclip from the cached CLI package.'
  } else {
    if (-not (Test-Path -LiteralPath $npxCmd)) { throw 'Node.js npx.cmd was not found.' }
    $arguments = "--yes --prefer-offline paperclipai@2026.1117.0 run --data-dir `"$dataDir`" --bind loopback --no-repair"
    Start-Process -FilePath $npxCmd -ArgumentList $arguments -WorkingDirectory $repoDir -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr | Out-Null
    Write-RunLog 'Started Paperclip through npx.'
  }
  for ($attempt = 0; $attempt -lt 36; $attempt++) {
    try {
      $null = Invoke-RestMethod -Uri $paperclipHealth -TimeoutSec 3
      $paperclipReady = $true
      break
    } catch {
      Start-Sleep -Seconds 5
    }
  }
}

if (-not $paperclipReady) { throw 'Paperclip did not become healthy within 180 seconds; inspect launcher-logs.' }
Write-RunLog 'Paperclip health check passed. No n8n schedule or agent routine was activated.'
