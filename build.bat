@echo off
setlocal

echo ======================================================
echo  PS5-REMOTE-PLAY  -  Windows .exe Builder
echo ======================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Install Python 3.10+ from https://www.python.org and try again.
    pause
    exit /b 1
)

echo Installing / updating build dependencies...
pip install -r requirements.txt pyinstaller --quiet
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Building executable (this may take a minute)...
echo.

:: Clean previous build
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

pyinstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name "PS5-REMOTE-PLAY" ^
    --add-data "src;src" ^
    --hidden-import av ^
    --hidden-import av.video ^
    --hidden-import av.audio ^
    --hidden-import av.codec ^
    --collect-all av ^
    main.py

if errorlevel 1 (
    echo.
    echo BUILD FAILED.
    pause
    exit /b 1
)

echo.
echo ======================================================
echo  SUCCESS
echo ======================================================
echo.
echo  Your executable is here:
echo    dist\PS5-REMOTE-PLAY.exe
echo.
echo  You can copy that .exe anywhere and run it.
echo  (First run may be slower while Windows Defender scans it.)
echo.
pause
