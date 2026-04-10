# Step 4 정답: week06 파이프라인을 Windows 작업 스케줄러에 등록
# 관리자 권한 PowerShell에서 실행하세요.
# 시연 PC에서만 등록하고, 강의가 끝나면 해제하세요:
#   Unregister-ScheduledTask -TaskName Week06Pipeline -Confirm:$false

$ErrorActionPreference = "Stop"

$TaskName = "Week06Pipeline"

# 이 스크립트(answers/register_task_answer.ps1)의 위치를 기준으로 경로 계산
$HerePath    = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot    = Resolve-Path (Join-Path $HerePath "..")
$PipelineSrc = Join-Path $RepoRoot "run_pipeline.py"
$WorkingDir  = $RepoRoot.Path

# 수강생이 Step 3에서 루트에 만들 run_pipeline.py가 없으면 정답 스크립트로 폴백
if (-not (Test-Path $PipelineSrc)) {
    Write-Warning "run_pipeline.py 가 루트에 없어서 answers/run_pipeline_answer.py 로 폴백합니다."
    $PipelineSrc = Join-Path $HerePath "run_pipeline_answer.py"
}

# Python 실행 파일 찾기 (py.exe 우선, 없으면 python.exe)
$PyPath = $null
foreach ($exe in @("py.exe", "python.exe")) {
    $cmd = Get-Command $exe -ErrorAction SilentlyContinue
    if ($cmd) { $PyPath = $cmd.Source; break }
}
if (-not $PyPath) {
    throw "Python 실행 파일(py.exe 또는 python.exe)을 PATH에서 찾지 못했습니다."
}

Write-Host "등록 내용:"
Write-Host "  Task Name : $TaskName"
Write-Host "  Python    : $PyPath"
Write-Host "  Script    : $PipelineSrc"
Write-Host "  WorkingDir: $WorkingDir"
Write-Host "  Trigger   : 매일 11:30"
Write-Host ""

$Action = New-ScheduledTaskAction `
    -Execute $PyPath `
    -Argument "`"$PipelineSrc`"" `
    -WorkingDirectory $WorkingDir

$Trigger = New-ScheduledTaskTrigger -Daily -At 11:30am

$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopOnIdleEnd `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

# 이미 등록돼 있으면 덮어쓰기
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Write-Host "기존 등록이 있어 해제 후 재등록합니다."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Week06 자동화 파이프라인 (매일 환율+매출 갱신)"

Write-Host ""
Write-Host "등록 완료. 지금 당장 한 번 돌려보려면:"
Write-Host "  Start-ScheduledTask -TaskName $TaskName"
Write-Host ""
Write-Host "해제하려면:"
Write-Host "  Unregister-ScheduledTask -TaskName $TaskName -Confirm:`$false"
