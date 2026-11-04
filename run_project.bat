@echo off
title Smart Crop AI - My-Project
echo ======================================================================
echo           SMART CROP AI: CROP DISEASE & RECOMMENDATION SYSTEM
echo ======================================================================
echo.
echo Launching Flask Web Application on http://127.0.0.1:5000 ...
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" app.py
) else (
    python app.py
)
pause
