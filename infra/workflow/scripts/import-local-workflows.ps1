$ErrorActionPreference = 'Stop'

$workflowDir = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
Push-Location $workflowDir
try {
  $workflowFiles = @(
    'faran-paperclip-health.local.json',
    'faran-agent-status.local.json',
    'faran-system-snapshot.local.json',
    'faran-task-monitor.local.json',
    'faran-evaluation-feed.local.json'
  )

  foreach ($file in $workflowFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $workflowDir "workflows\$file"))) {
      throw "Workflow definition not found: $file"
    }
    docker compose --env-file .env -f compose.yaml -f compose.local.yaml exec n8n n8n import:workflow "--input=/workflows/$file"
    if ($LASTEXITCODE -ne 0) { throw "n8n import failed for $file" }
    Write-Output "Imported/updated inactive workflow: $file"
  }
} finally {
  Pop-Location
}
