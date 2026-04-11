@echo off
REM Run Court locally, with Ollama launcher support
if "%COURT_MODEL%"=="" set COURT_MODEL=court-refusal-v1
python launcher.py
pause
