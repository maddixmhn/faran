$ErrorActionPreference = 'Stop'
$taskName = 'Faran Local Workflow Runtime'
$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($null -ne $task) {
  Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
  Write-Output "Removed '$taskName'. Running containers and Paperclip process were not stopped."
} else {
  Write-Output "'$taskName' is not installed."
}
