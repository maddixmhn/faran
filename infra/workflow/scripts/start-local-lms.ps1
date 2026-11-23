param(
    [string]$Image = 'moodlehq/moodle-php-apache:8.3',
    [switch]$DatabaseOnly,
    [switch]$Install
)

$ErrorActionPreference = 'Stop'
$workflowDir = Split-Path -Parent $PSScriptRoot
$localDir = Join-Path $workflowDir 'data/lms'
$sourceDir = Join-Path $localDir 'moodle'
if (-not $DatabaseOnly -and -not (Test-Path (Join-Path $sourceDir 'admin/cli/install.php'))) {
    throw 'Moodle source is incomplete. Finish the upstream download first.'
}

$secretFile = Join-Path $localDir 'compose.env'
if (-not (Test-Path $secretFile)) {
    $random = [byte[]]::new(32)
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($random) } finally { $rng.Dispose() }
    $password = [Convert]::ToBase64String($random)
    [IO.File]::WriteAllText($secretFile, "FARAN_LMS_DB_PASSWORD=$password"+[Environment]::NewLine)
}

$env:FARAN_LMS_IMAGE = $Image
$compose = @('--env-file', $secretFile, '-f', (Join-Path $workflowDir 'compose.lms.yaml'))
if ($DatabaseOnly) {
    docker compose @compose up -d --wait db
    if ($LASTEXITCODE -ne 0) { throw 'The Moodle database did not start.' }
    return
}
docker compose @compose up -d --wait
if ($LASTEXITCODE -ne 0) { throw 'The Moodle containers did not start.' }
docker compose @compose exec -T -u root lms chown www-data:www-data /var/www/moodledata
if ($LASTEXITCODE -ne 0) { throw 'Could not prepare the Moodle data directory.' }
if ($Install -and -not (Test-Path (Join-Path $sourceDir 'config.php'))) {
    $dbPassword = (Get-Content -LiteralPath $secretFile -Raw).Trim().Split('=', 2)[1]
    $adminFile = Join-Path $localDir 'moodle-admin.env'
    if (-not (Test-Path $adminFile)) {
        $adminPassword = 'Aa9!' + [Guid]::NewGuid().ToString('N')
        [IO.File]::WriteAllText($adminFile, "MOODLE_ADMIN_PASSWORD=$adminPassword" + [Environment]::NewLine)
    }
    $adminPassword = (Get-Content -LiteralPath $adminFile -Raw).Trim().Split('=', 2)[1]
    docker compose @compose exec -T -u www-data lms php /var/www/html/admin/cli/install.php --non-interactive --agree-license --wwwroot=http://localhost:8700 --dataroot=/var/www/moodledata --dbtype=pgsql --dbhost=db --dbname=moodle --dbuser=moodle "--dbpass=$dbPassword" "--fullname=Faran University" "--shortname=Faran" --adminuser=admin "--adminpass=$adminPassword" --adminemail=admin@example.invalid
    if ($LASTEXITCODE -ne 0) { throw 'Moodle CLI installation failed; inspect the installer output before retrying.' }
}
Write-Output 'Moodle installer: http://localhost:8700/'
Write-Output "Local PostgreSQL settings file: $secretFile"
