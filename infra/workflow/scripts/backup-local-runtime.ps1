param(
    [string]$PaperclipDataDir = "infra/workflow/data/paperclip-sandbox"
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$workflowDir = Join-Path $repoRoot 'infra\workflow'
$paperclipRoot = Join-Path $repoRoot $PaperclipDataDir
$instanceDir = Join-Path $paperclipRoot 'instances\default'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupDir = Join-Path $workflowDir "data\backups\$stamp"
$identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

if (-not (Test-Path (Join-Path $workflowDir '.env'))) { throw 'infra/workflow/.env is required.' }
if (-not (Test-Path (Join-Path $instanceDir 'config.json'))) { throw 'Paperclip instance config was not found.' }
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw 'Docker CLI was not found.' }

New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
& icacls $backupDir /inheritance:r /grant:r "${identity}:(OI)(CI)F" | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Could not restrict backup folder permissions to the current Windows account.' }

try {
    $paperclipBackup = Join-Path $backupDir 'paperclip-db'
    New-Item -ItemType Directory -Path $paperclipBackup | Out-Null
    $cli = Get-Command paperclipai -ErrorAction SilentlyContinue
    if ($cli) {
        & $cli.Source db:backup --data-dir $paperclipRoot --dir $paperclipBackup --json | Out-Null
    } else {
        $cachedCli = Get-ChildItem "$env:LOCALAPPDATA\npm-cache\_npx" -Directory -ErrorAction SilentlyContinue |
            ForEach-Object { Join-Path $_.FullName 'node_modules\paperclipai\dist\index.js' } |
            Where-Object { Test-Path $_ } |
            Select-Object -First 1
        if ($cachedCli) {
            & node $cachedCli db:backup --data-dir $paperclipRoot --dir $paperclipBackup --json | Out-Null
        } else {
            & npx --yes --package paperclipai@2026.1117.0 paperclipai db:backup --data-dir $paperclipRoot --dir $paperclipBackup --json | Out-Null
        }
    }
    if ($LASTEXITCODE -ne 0) { throw 'Paperclip database backup failed.' }

    $paperclipFiles = Join-Path $backupDir 'paperclip-instance'
    New-Item -ItemType Directory -Path $paperclipFiles | Out-Null
    Copy-Item (Join-Path $instanceDir 'config.json') $paperclipFiles
    Copy-Item (Join-Path $instanceDir '.env') $paperclipFiles -ErrorAction SilentlyContinue
    Copy-Item (Join-Path $instanceDir 'secrets') (Join-Path $paperclipFiles 'secrets') -Recurse
    $storage = Join-Path $instanceDir 'data\storage'
    if (Test-Path $storage) { Copy-Item $storage (Join-Path $paperclipFiles 'storage') -Recurse }

    $compose = @('--env-file', (Join-Path $workflowDir '.env'), '-f', (Join-Path $workflowDir 'compose.yaml'), '-f', (Join-Path $workflowDir 'compose.local.yaml'))
    $dbName = & docker compose @compose ps -q n8n-db
    if ($LASTEXITCODE -ne 0 -or -not $dbName) { throw 'n8n PostgreSQL container is not running.' }
    $n8nName = & docker compose @compose ps -q n8n
    if ($LASTEXITCODE -ne 0 -or -not $n8nName) { throw 'n8n container is not running.' }

    & docker exec $dbName pg_dump -U n8n -d n8n -Fc -f /tmp/faran-n8n.dump
    if ($LASTEXITCODE -ne 0) { throw 'n8n PostgreSQL dump failed.' }
    & docker cp "${dbName}:/tmp/faran-n8n.dump" (Join-Path $backupDir 'n8n-db.dump') | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Could not copy the n8n database dump.' }
    & docker exec $n8nName tar -czf /tmp/faran-n8n-data.tgz -C /home/node/.n8n .
    if ($LASTEXITCODE -ne 0) { throw 'n8n persistent data archive failed.' }
    & docker cp "${n8nName}:/tmp/faran-n8n-data.tgz" (Join-Path $backupDir 'n8n-data.tgz') | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Could not copy the n8n persistent data archive.' }

    Copy-Item (Join-Path $workflowDir '.env') (Join-Path $backupDir 'workflow.env')
    $manifest = [ordered]@{
        createdAt = (Get-Date).ToString('o')
        scope = 'Local Paperclip and n8n recovery bundle; contains secrets and credentials'
        paperclipDataDir = $PaperclipDataDir
        n8nDatabase = 'n8n-db.dump (PostgreSQL custom format)'
        n8nPersistentData = 'n8n-data.tgz (includes the credential encryption key)'
        paperclipDatabase = 'paperclip-db/*.sql.gz'
        restoreNote = 'Keep the SQL archives, encryption keys and env files together; restrict access to this directory.'
    }
    $manifest | ConvertTo-Json | Set-Content (Join-Path $backupDir 'manifest.json') -Encoding utf8
    Get-ChildItem $backupDir -Recurse -File | ForEach-Object {
        [pscustomobject]@{ path = $_.FullName.Substring($backupDir.Length + 1); bytes = $_.Length; sha256 = (Get-FileHash $_.FullName -Algorithm SHA256).Hash }
    } | ConvertTo-Json -Depth 3 | Set-Content (Join-Path $backupDir 'checksums.json') -Encoding utf8
    Write-Output "Backup created: $backupDir"
} catch {
    Write-Error "Backup incomplete at $backupDir. Do not use it for recovery until rerun succeeds. $($_.Exception.Message)"
    throw
}
