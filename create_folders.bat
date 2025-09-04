@echo off
echo Creating folder structure for Dynamic Firewall...

REM Create main directories
mkdir app
mkdir app\core
mkdir app\ai
mkdir app\ai\models
mkdir app\deception
mkdir app\network
mkdir app\dashboard
mkdir app\dashboard\components
mkdir app\dashboard\static
mkdir app\dashboard\static\css
mkdir app\dashboard\static\js
mkdir app\dashboard\static\images
mkdir app\dashboard\templates
mkdir app\utils
mkdir app\tests

REM Create data directories
mkdir data
mkdir data\logs
mkdir data\config
mkdir data\training_data
mkdir data\backups

REM Create other directories
mkdir scripts
mkdir docs
mkdir docker
mkdir docker\nginx
mkdir docker\nginx\ssl
mkdir requirements
mkdir examples
mkdir models

echo Folder structure created successfully!
pause
