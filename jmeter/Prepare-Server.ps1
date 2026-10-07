param([Parameter(Mandatory=$true)][string]$RunId, [switch]$Apply)
$ErrorActionPreference = 'Stop'
if ($RunId -notmatch '^[A-Za-z0-9][A-Za-z0-9_-]*$') { throw 'Invalid RunId' }
$repo = Split-Path $PSScriptRoot -Parent
$runPath = Join-Path $PSScriptRoot "runs\$RunId"
$manifest = Get-Content (Join-Path $runPath 'manifest.json') -Raw | ConvertFrom-Json
if (-not $Apply) {
    Write-Host "PREVIEW ONLY: configure service for $($manifest.model_tag), separate database/logs for $RunId."
    Write-Host 'No containers changed and no HTTP requests sent. Use -Apply later on Computer A.'
    exit 0
}
if (Test-Path (Join-Path $runPath 'server-ready.json')) { throw 'Server already prepared. Use a new RunId for another attempt.' }
if (Test-Path (Join-Path $runPath 'service-data/tickets.sqlite3')) { throw 'Database is not fresh. Use a new RunId.' }
Push-Location $repo
try {
    # Read local model metadata through the existing service container; no inference.
    $readTags = 'import os,requests,json; print(json.dumps(requests.get(os.environ["OLLAMA_BASE_URL"]+"/api/tags",timeout=10).json()))'
    $raw = $readTags | & docker compose exec -T service python -
    if ($LASTEXITCODE -ne 0) { throw 'Cannot read model metadata; start the existing Compose stack first.' }
    $model = ($raw | ConvertFrom-Json).models | Where-Object { $_.name -eq $manifest.model_tag }
    if (-not $model -or "sha256:$($model.digest -replace '^sha256:','')" -ne $manifest.model_digest) {
        throw "Missing or mismatched pinned model. Pull $($manifest.model_tag) and recheck its digest."
    }
    New-Item -ItemType Directory -Force (Join-Path $runPath 'service-data'),(Join-Path $runPath 'service-logs') | Out-Null
    $env:SERVICE_BIND_ADDRESS = '0.0.0.0'
    $env:SERVICE_PORT = '18000'
    $override = Join-Path $runPath 'server.override.json'
    & docker compose -f docker-compose.yml -f $override up -d --no-deps --force-recreate service
    if ($LASTEXITCODE -ne 0) { throw 'Service recreation failed' }
    $stats = $null
    for ($attempt = 0; $attempt -lt 10; $attempt++) {
        try { $stats = Invoke-RestMethod 'http://127.0.0.1:18000/stats' -TimeoutSec 5; break }
        catch { Start-Sleep -Seconds 1 }
    }
    if ($null -eq $stats -or $stats.total -ne 0) { throw 'Fresh database readiness check failed' }
    $record = [ordered]@{
        run_id=$RunId; model_tag=$manifest.model_tag; model_digest=$manifest.model_digest
        captured_utc=[DateTime]::UtcNow.ToString('o'); computer=$env:COMPUTERNAME
        cpu=@(Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors)
        memory_bytes=(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
        os=(Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version)
        docker_info=@(& docker info --format '{{json .}}')
        git_revision=(& git rev-parse HEAD); git_status=@(& git status --short)
        initial_stats=$stats; model_metadata=$model
        service_packages=@(& docker compose exec -T service python -m pip freeze)
    }
    $record | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $runPath 'server-ready.json') -Encoding UTF8
} finally { Pop-Location }
Write-Host 'Server prepared. No classification or load test started. Copy server-ready.json to Computer B.'
