# 🧬 SkinEngine "One-Click" Auto-Deploy v1.0
# 사용법: .\deploy.ps1

$serverIp = "72.62.254.119"
$serverPath = "/root/SkinEngine"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Clear-Host
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   🚀 SkinEngine One-Click Deployment       " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Start Time: $timestamp`n"

# 1. Local Git Commit
Write-Host "📦 [1/3] Local Git 커밋 중..." -ForegroundColor Yellow
git add .
$commitMsg = "Deploy: $timestamp"
git commit -m "$commitMsg"

# 2. Push to GitHub
Write-Host "`n📤 [2/3] GitHub로 푸시 중..." -ForegroundColor Yellow
git push origin main

# 3. Server Sync & Service Restart
Write-Host "`n🔄 [3/3] 서버 동기화 및 시스템 서비스 재시작 중..." -ForegroundColor Yellow
$remoteCmd = @"
cd $serverPath && \
git fetch --all && \
git reset --hard origin/main && \
sudo systemctl daemon-reload && \
sudo systemctl restart skinengine && \
systemctl restart nginx
"@

ssh root@$serverIp $remoteCmd

Write-Host "`n"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ✅ SkinEngine 배포 및 서비스 재시작 완료! " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
