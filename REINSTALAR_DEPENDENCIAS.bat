@echo off
setlocal
cd /d "%~dp0"
title VisorXM - Reparar entorno
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\bootstrap.ps1" -ForceInstall
set "VX_EXIT=%ERRORLEVEL%"
if not "%VX_EXIT%"=="0" pause
exit /b %VX_EXIT%
