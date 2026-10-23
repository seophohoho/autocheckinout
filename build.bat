@echo off
rem Double-click to build dist\ (runs build.ps1)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build.ps1"
pause
