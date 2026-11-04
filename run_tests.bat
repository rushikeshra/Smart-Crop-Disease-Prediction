@echo off
title Run Verification Tests - My-Project
echo ======================================================================
echo                  RUNNING AUTOMATED TEST SUITE
echo ======================================================================
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" -m unittest test_app.py
) else (
    python -m unittest test_app.py
)
pause
