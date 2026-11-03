@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 start.py %*
) else (
  where python >nul 2>nul
  if not errorlevel 1 (
    python start.py %*
  ) else (
    echo Python 3.11+ requis / required: https://www.python.org/downloads/
    pause
  )
)
endlocal
