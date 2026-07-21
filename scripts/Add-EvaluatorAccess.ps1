#!/usr/bin/env pwsh
# Add-EvaluatorAccess.ps1
# 批量添加 GitHub 评委为协作者
#
# 用法：
#   1. 编辑下方 $evaluators 列表，添加评委的 GitHub 用户名和真实姓名
#   2. 在 PowerShell 中运行：.\Add-EvaluatorAccess.ps1
#
# 前置要求：
#   - gh CLI 已安装并登录（gh auth status 验证）
#   - 当前用户是仓库 owner

param(
    [string[]]$Usernames = @()
)

$repo = "yigenfeng0707-netizen/TsinghuaEmbodiedAI"
$ghPath = "C:\Program Files\GitHub CLI\gh.exe"

# 默认评委列表（编辑这里）
$defaultEvaluators = @(
    # @{
    #     Username = "evaluator1-github-username"
    #     Name = "真实姓名"
    #     Affiliation = "所属单位"
    # },
)

if ($Usernames.Count -eq 0) {
    $evaluators = $defaultEvaluators
} else {
    $evaluators = $Usernames | ForEach-Object { @{ Username = $_; Name = "N/A"; Affiliation = "N/A" } }
}

if ($evaluators.Count -eq 0) {
    Write-Host "未提供评委列表。退出。" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "用法 1：编辑脚本中的 `$defaultEvaluators 列表" -ForegroundColor Cyan
    Write-Host "用法 2：命令行参数 -Usernames user1,user2,user3" -ForegroundColor Cyan
    exit 0
}

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "批量添加 GitHub 评委" -ForegroundColor Cyan
Write-Host "仓库：$repo" -ForegroundColor Cyan
Write-Host "评委数量：$($evaluators.Count)" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# 验证仓库当前可见性
$visibility = & $ghPath repo view $repo --json visibility --jq ".visibility" 2>&1
Write-Host "当前可见性：$visibility" -ForegroundColor Yellow
if ($visibility -ne "PRIVATE") {
    Write-Host "警告：仓库不是私有状态！" -ForegroundColor Red
}

# 发送邀请
$success = 0
$failed = @()

foreach ($eval in $evaluators) {
    $username = $eval.Username
    Write-Host "正在添加 $username ..." -NoNewline

    try {
        # 发送协作者邀请
        $result = & $ghPath api -X PUT "/repos/$repo/collaborators/$username" -f permission=pull 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host " OK" -ForegroundColor Green
            Write-Host "  邀请已发送，等待 $username 接受" -ForegroundColor Green
            $success++
        } else {
            Write-Host " FAILED" -ForegroundColor Red
            Write-Host "  错误：$result" -ForegroundColor Red
            $failed += $username
        }
    } catch {
        Write-Host " EXCEPTION" -ForegroundColor Red
        Write-Host "  异常：$_" -ForegroundColor Red
        $failed += $username
    }
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "完成" -ForegroundColor Cyan
Write-Host "  成功：$success / $($evaluators.Count)" -ForegroundColor $(if ($success -eq $evaluators.Count) { "Green" } else { "Yellow" })

if ($failed.Count -gt 0) {
    Write-Host "  失败：$($failed -join ', ')" -ForegroundColor Red
}

Write-Host ""
Write-Host "评委需访问 https://github.com/$repo 接受邀请" -ForegroundColor Cyan
Write-Host "查看所有待处理邀请：" -ForegroundColor Cyan
Write-Host "  gh api /repos/$repo/invitations --jq '.[].invitee.login'" -ForegroundColor Gray
