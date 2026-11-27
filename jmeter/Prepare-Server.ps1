param([Parameter(Mandatory=$true)][string]$RunId, [switch]$Apply, [switch]$Finish)
$ErrorActionPreference = 'Stop'
if ($RunId -notmatch '^[A-Za-z0-9][A-Za-z0-9_-]*$') { throw 'Invalid RunId' }
$repo = Split-Path $PSScriptRoot -Parent
$runPath = Join-Path $PSScriptRoot "runs\$RunId"
$manifest = Get-Content (Join-Path $runPath 'manifest.json') -Raw | ConvertFrom-Json
$a2 = $manifest.profile -eq 'a2-speed'
if ($Finish) {
    # After the client run: the rise in the stats total is what the service completed and stored.
    $ready = Get-Content (Join-Path $runPath 'server-ready.json') -Raw | ConvertFrom-Json
    $stats = Invoke-RestMethod 'http://127.0.0.1:18000/stats' -TimeoutSec 30
    Push-Location $repo
    try { $loaded = @(& docker compose exec -T ollama ollama ps) } finally { Pop-Location }
    [ordered]@{
        run_id=$RunId; captured_utc=[DateTime]::UtcNow.ToString('o')
        stats_before_run=$ready.stats_before_run; stats_after_run=$stats.total
        completed_and_stored=$stats.total - $ready.stats_before_run; ollama_ps=$loaded
    } | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $runPath 'server-finish.json') -Encoding UTF8
    Write-Host "Stored during the run: $($stats.total - $ready.stats_before_run). Copy server-finish.json and service-logs to Computer B."
    exit 0
}
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
    $expected = @($manifest.model_tag)
    if ($a2 -and $manifest.large_model_tag) {
        $large = ($raw | ConvertFrom-Json).models | Where-Object { $_.name -eq $manifest.large_model_tag }
        if (-not $large -or "sha256:$($large.digest -replace '^sha256:','')" -ne $manifest.large_model_digest) {
            throw "Missing or mismatched pinned model. Pull $($manifest.large_model_tag) and recheck its digest."
        }
        $expected += $manifest.large_model_tag
    }
    if ($a2) {
        # Clears Ollama's prompt cache and unloads every model before the run.
        & docker compose restart ollama
        if ($LASTEXITCODE -ne 0) { throw 'Ollama restart failed' }
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
    if ($a2) {
        $loaded = @()
        for ($attempt = 0; $attempt -lt 30; $attempt++) {
            $loaded = @(& docker compose exec -T ollama ollama ps | Where-Object { "$_".Trim() })
            if ($LASTEXITCODE -eq 0) { break }
            Start-Sleep -Seconds 1
        }
        if ($LASTEXITCODE -ne 0) { throw 'Ollama did not come back after the restart' }
        if ($loaded.Count -gt 1) { throw 'A model is still loaded after the Ollama restart' }
        $warmup = Get-Content (Join-Path $runPath 'data\warmup.json') -Raw | ConvertFrom-Json
        foreach ($ticket in $warmup) {
            $body = [Text.Encoding]::UTF8.GetBytes((@{narrative=$ticket.narrative} | ConvertTo-Json -Compress))
            Invoke-RestMethod 'http://127.0.0.1:18000/tickets' -Method Post -Body $body `
                -ContentType 'application/json; charset=utf-8' -TimeoutSec 900 | Out-Null
        }
        if ($manifest.large_model_tag) {
            # The rule may not escalate any warm-up ticket, so load the large model directly,
            # with the service's own load options. This call is not in the service log.
            $b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($warmup[0].narrative))
            $warmLarge = 'import os,requests,base64; requests.post(os.environ["OLLAMA_BASE_URL"]+"/api/chat",json={"model":"' +
                $manifest.large_model_tag + '","stream":False,"options":{"temperature":0,"num_gpu":0},"messages":[{"role":"user","content":base64.b64decode("' +
                $b64 + '").decode()}]},timeout=900).raise_for_status()'
            $warmLarge | & docker compose exec -T service python -
            if ($LASTEXITCODE -ne 0) { throw 'Large-model warm-up failed' }
        }
        $loaded = @(& docker compose exec -T ollama ollama ps)
        $loaded | Set-Content (Join-Path $runPath 'ollama-ps-before-run.txt') -Encoding UTF8
        foreach ($tag in $expected) {
            if (-not ($loaded | Where-Object { "$_".StartsWith("$tag ") })) { throw "$tag is not loaded after warm-up. Do not start the run." }
        }
        $stats = Invoke-RestMethod 'http://127.0.0.1:18000/stats' -TimeoutSec 30
    }
    $record = [ordered]@{
        run_id=$RunId; model_tag=$manifest.model_tag; model_digest=$manifest.model_digest
        captured_utc=[DateTime]::UtcNow.ToString('o'); computer=$env:COMPUTERNAME
        cpu=@(Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors)
        memory_bytes=(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
        os=(Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version)
        docker_info=@(& docker info --format '{{json .}}')
        git_revision=(& git rev-parse HEAD); git_status=@(& git status --short)
        initial_stats=$stats; stats_before_run=$stats.total; model_metadata=$model
        service_packages=@(& docker compose exec -T service python -m pip freeze)
    }
    $record | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $runPath 'server-ready.json') -Encoding UTF8
} finally { Pop-Location }
if ($a2) {
    Write-Host "Server prepared and warmed up: $($expected -join ', ') loaded. No load test started."
    Write-Host 'Copy server-ready.json to Computer B and start the run within 4 minutes: Ollama unloads an idle model after 5.'
} else {
    Write-Host 'Server prepared. No classification or load test started. Copy server-ready.json to Computer B.'
}
