$ErrorActionPreference = 'Stop'

$workflowDir = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$launcher = Join-Path $PSScriptRoot 'start-local-runtime.ps1'
$taskName = 'Faran Local Workflow Runtime'
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$powershellExe = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'

$action = New-ScheduledTaskAction -Execute $powershellExe -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$launcher`"" -WorkingDirectory $workflowDir
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $currentUser
$principal = New-ScheduledTaskPrincipal -UserId $currentUser -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 2)

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description 'Starts the local Faran Paperclip and n8n sandbox when this user signs in. Agent routines remain disabled.' -Force | Out-Null
Write-Output "Registered '$taskName' for $currentUser (interactive logon only; no password stored)."
