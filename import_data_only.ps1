# import_data_only.ps1
# Extracts only DATA (COPY...\.  blocks) from a pg_dump SQL file and imports to Neon
# Usage: .\import_data_only.ps1

$sqlFile = ".\kenya_health_complete.sql"
$connStr = "postgresql://neondb_owner:npg_hy0MECSck1GY@ep-cold-brook-ageakz88-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require"
$psql = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
$tempFile = "$env:TEMP\neon_data_import.sql"

Write-Host "Reading dump file..." -ForegroundColor Cyan
$lines = [System.IO.File]::ReadAllLines((Resolve-Path $sqlFile))
Write-Host "Total lines: $($lines.Count)" -ForegroundColor Cyan

# Extract COPY blocks only
$output = [System.Collections.Generic.List[string]]::new()
$output.Add("SET session_replication_role = replica;") # Disable FK checks during import
$inCopy = $false

foreach ($line in $lines) {
    if ($line -match '^COPY ') {
        $inCopy = $true
        $output.Add($line)
    } elseif ($inCopy) {
        $output.Add($line)
        if ($line -eq '\.') {
            $inCopy = $false
        }
    }
}

$output.Add("SET session_replication_role = DEFAULT;")
$output.Add("") # trailing newline

Write-Host "Extracted $($output.Count) lines of COPY data" -ForegroundColor Green
[System.IO.File]::WriteAllLines($tempFile, $output)

Write-Host "Importing data to Neon..." -ForegroundColor Cyan
& $psql $connStr -P pager=off -f $tempFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Import complete!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Import failed (exit code $LASTEXITCODE)" -ForegroundColor Red
}

# Cleanup
Remove-Item $tempFile -ErrorAction SilentlyContinue
