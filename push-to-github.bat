@echo off
REM ============================================
REM Push Holographic-Biology to GitHub
REM Run this when you have network access to GitHub
REM ============================================

cd /d D:\obsidian\Holographic-Biology

REM Set up remote (first time only)
git remote set-url origin https://github.com/laimengjun/holographic-biology.git 2>nul
if %errorlevel% neq 0 (
    git remote add origin https://github.com/laimengjun/holographic-biology.git
)

REM Push main branch + tags
git push -u origin main --tags

echo.
echo Done! Check: https://github.com/laimengjun/holographic-biology
pause
