# Scan Local Development Directory
# Triggers ParallelDev to scan d:\dev for projects

$scanDirectory = "d:\dev"
$apiUrl = "http://localhost:8000/api/scan"

Write-Host "Scanning directory: $scanDirectory" -ForegroundColor Cyan
Write-Host "This may take a few moments..." -ForegroundColor Yellow
Write-Host ""

try {
    $body = @{
        directory = $scanDirectory
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Body $body -ContentType "application/json"

    Write-Host "Scan completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Results:" -ForegroundColor Cyan
    Write-Host "  Projects found: $($response.data.projects_found)" -ForegroundColor White
    Write-Host "  Projects saved: $($response.data.projects_saved)" -ForegroundColor White
    Write-Host ""

    if ($response.data.projects_found -gt 0) {
        Write-Host "View your projects at: http://localhost:8001" -ForegroundColor Green
    } else {
        Write-Host "No projects found. Make sure your projects have REQUIREMENTS.md, TODO.md, or README.md files." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Error scanning directory:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure the backend is running (.\start-backend.bat)" -ForegroundColor Yellow
    exit 1
}
