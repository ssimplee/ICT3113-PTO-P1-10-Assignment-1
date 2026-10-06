param(
    [Parameter(Mandatory=$true)][string]$RunId,
    [string]$JMeter = "$env:USERPROFILE\Tools\apache-jmeter-5.6.3\bin\jmeter.bat",
    [switch]$Start
)
$ErrorActionPreference = 'Stop'
if ($RunId -notmatch '^[A-Za-z0-9][A-Za-z0-9_-]*$') { throw 'Invalid RunId' }
$runPath = Join-Path $PSScriptRoot "runs\$RunId"
$manifest = Get-Content (Join-Path $runPath 'manifest.json') -Raw | ConvertFrom-Json
if (-not $Start) {
    Write-Host "PREVIEW ONLY: $($manifest.profile), $($manifest.model_tag), host $($manifest.host)."
    Write-Host 'No traffic sent. After server preparation and validation, add -Start to execute.'
    exit 0
}
if (-not (Test-Path -LiteralPath $JMeter)) { throw "JMeter not found: $JMeter" }
if (Test-Path (Join-Path $runPath 'client-start.json')) { throw 'Run already attempted. Prepare a new RunId.' }
$readyFile = Join-Path $runPath 'server-ready.json'
if (-not (Test-Path $readyFile)) { throw 'Copy server-ready.json from Computer A after Prepare-Server.ps1 -Apply.' }
$ready = Get-Content $readyFile -Raw | ConvertFrom-Json
if ($ready.model_digest -ne $manifest.model_digest -or $ready.run_id -ne $RunId) { throw 'Server readiness does not match run' }
foreach ($property in $manifest.file_sha256.PSObject.Properties) {
    $actual = (Get-FileHash -LiteralPath (Join-Path $runPath $property.Name) -Algorithm SHA256).Hash.ToLower()
    if ($actual -ne $property.Value) { throw "Changed prepared file: $($property.Name). Prepare a new bundle." }
}
# Windows PowerShell treats Java's version output on stderr as error records.
$ErrorActionPreference = 'Continue'
$javaVersion = @(& java -version 2>&1 | ForEach-Object { "$_" })
$jmeterVersion = @(& $JMeter -v 2>&1 | ForEach-Object { "$_" })
$ErrorActionPreference = 'Stop'
$capture = [ordered]@{
    run_id = $RunId
    launch_utc = [DateTime]::UtcNow.ToString('o')
    computer = $env:COMPUTERNAME
    cpu = @(Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors)
    memory_bytes = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
    os = (Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version)
    git_revision = (git -C $PSScriptRoot rev-parse HEAD)
    git_status = @(git -C $PSScriptRoot status --short)
    java = $javaVersion
    jmeter = $jmeterVersion
}
$capture | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $runPath 'client-start.json') -Encoding UTF8
Push-Location $runPath
try {
    & $JMeter -n -t plan.jmx -q results.properties -l results.jtl -j jmeter.log
    $runExit = $LASTEXITCODE
    @{finished_utc=[DateTime]::UtcNow.ToString('o'); exit_code=$runExit} |
        ConvertTo-Json | Set-Content 'client-finish.json' -Encoding UTF8
    if ($runExit -ne 0) { throw "JMeter exited with code $runExit; preserve the failed run." }
} finally { Pop-Location }
Write-Host 'Run ended. Copy matching server logs and inspect errors/backlog before the next run.'
