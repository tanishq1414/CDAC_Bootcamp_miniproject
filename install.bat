@echo off
echo Installing Dynamic Firewall with AI Deceptive Layer...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set pyversion=%%i
for /f "tokens=1,2,3 delims=." %%a in ("%pyversion%") do (
    if %%a lss 3 (
        echo Python 3.8 or higher is required. Found version: %pyversion%
        pause
        exit /b 1
    )
    if %%a equ 3 if %%b lss 8 (
        echo Python 3.8 or higher is required. Found version: %pyversion%
        pause
        exit /b 1
    )
)

echo Found Python version: %pyversion%
echo.

REM Create necessary directories
echo Creating folder structure...
if not exist "app" mkdir app
if not exist "app\core" mkdir app\core
if not exist "app\ai" mkdir app\ai
if not exist "app\ai\models" mkdir app\ai\models
if not exist "app\deception" mkdir app\deception
if not exist "app\network" mkdir app\network
if not exist "app\dashboard" mkdir app\dashboard
if not exist "app\dashboard\components" mkdir app\dashboard\components
if not exist "app\dashboard\static" mkdir app\dashboard\static
if not exist "app\dashboard\static\css" mkdir app\dashboard\static\css
if not exist "app\dashboard\static\js" mkdir app\dashboard\static\js
if not exist "app\dashboard\static\images" mkdir app\dashboard\static\images
if not exist "app\dashboard\templates" mkdir app\dashboard\templates
if not exist "app\utils" mkdir app\utils
if not exist "app\tests" mkdir app\tests

if not exist "data" mkdir data
if not exist "data\logs" mkdir data\logs
if not exist "data\config" mkdir data\config
if not exist "data\training_data" mkdir data\training_data
if not exist "data\backups" mkdir data\backups

if not exist "scripts" mkdir scripts
if not exist "docs" mkdir docs
if not exist "docker" mkdir docker
if not exist "docker\nginx" mkdir docker\nginx
if not exist "docker\nginx\ssl" mkdir docker\nginx\ssl
if not exist "requirements" mkdir requirements
if not exist "examples" mkdir examples
if not exist "models" mkdir models

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    echo Try running: python -m ensurepip
    pause
    exit /b 1
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

REM Install dependencies
echo Installing Python dependencies...
pip install --upgrade pip
if errorlevel 1 (
    echo Failed to upgrade pip.
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    echo Trying individual installation...
    pip install flask==2.3.3
    pip install cryptography==41.0.4
    pip install requests==2.31.0
    pip install pyqt5==5.15.9
    pip install qdarkstyle==3.1
    pip install scikit-learn==1.3.0
    pip install pandas==2.0.3
    pip install numpy==1.24.3
)

REM Create default config
echo Creating default configuration...
python -c "from app.config import Config; Config.save_config(); print('Default configuration created.')"

echo.
echo Installation complete!
echo.
echo To start the application, run: scripts\start.bat
echo.
pause