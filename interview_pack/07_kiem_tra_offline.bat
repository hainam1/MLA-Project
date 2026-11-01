@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 goto usepy
python -I "%~dp0_phu\_cong_cu\run_offline.py"
goto done
:usepy
where py >nul 2>nul
if errorlevel 1 goto missing
py -3 -I "%~dp0_phu\_cong_cu\run_offline.py"
goto done
:missing
echo Python is required. Install Python before running these offline checks.
:done
echo.
pause
endlocal
