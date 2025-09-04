@echo off
echo Starting Dynamic Firewall System...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Running install script...
    call scripts\install.bat
    if errorlevel 1 (
        echo Installation failed.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment.
    echo Trying alternative activation...
    call venv\Scripts\activate
    if errorlevel 1 (
        echo Still failed to activate virtual environment.
        pause
        exit /b 1
    )
)

REM Start the application
echo Starting application...
python app\main.py

pause