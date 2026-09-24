@echo off
setlocal
cd /d "%~dp0"
title VisorXM

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\bootstrap.ps1"
set "VX_EXIT=%ERRORLEVEL%"

if not "%VX_EXIT%"=="0" (
    echo.
    echo VisorXM encontro un problema durante la instalacion o el inicio.
    echo Revisa VisorXM_instalacion.log si necesitas el detalle tecnico.
    echo.
    pause
)

exit /b %VX_EXIT%
