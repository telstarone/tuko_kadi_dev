# scripts/verify_environment.ps1
Write-Host '=== Sauti ya Mwananchi — Environment Verification ===' -ForegroundColor Cyan

$checks = @(
    @{ Name = 'Python'; Cmd = 'python --version' },
    @{ Name = 'pip';    Cmd = 'python -m pip --version' },
    @{ Name = 'Git';    Cmd = 'git --version' },
    @{ Name = 'Gcloud'; Cmd = 'gcloud --version' },
    @{ Name = 'Docker'; Cmd = 'docker --version' },
    @{ Name = 'ngrok';  Cmd = 'ngrok --version' }
)

$failed = @()
foreach ($check in $checks) {
    $name = $check.Name
    $cmd = $check.Cmd
    try {
        $output = Invoke-Expression $cmd 2>&1 | Select-Object -First 1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[PASS] $name : $output" -ForegroundColor Green
        } else {
            Write-Host "[FAIL] $name" -ForegroundColor Red
            $failed += $name
        }
    } catch {
        Write-Host "[FAIL] $name" -ForegroundColor Red
        $failed += $name
    }
}

if ($failed.Count -gt 0) {
    Write-Host 'Missing tools detected.' -ForegroundColor Red
} else {
    Write-Host 'All tools verified.' -ForegroundColor Green
}
