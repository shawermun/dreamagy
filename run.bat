@echo off
cd /d "%~dp0"
if exist "C:\Users\Artem\miniconda3\pythonw.exe" (
    start "" "C:\Users\Artem\miniconda3\pythonw.exe" main.py
) else (
    start "" pythonw main.py
)
