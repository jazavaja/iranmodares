@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
python iran2.py
pause