@echo off
echo ========================================
echo    Peak3 Requirements Automation Demo
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if required packages are installed
echo 🔍 Checking dependencies...
python -c "import flask, flask_cors, requests, pandas, openpyxl, pyyaml" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Some dependencies are missing. Installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
) else (
    echo ✅ All dependencies are available
)

echo.
echo 🚀 Starting Peak3 Requirements Automation Demo...
echo.
echo 📋 Instructions:
echo    1. Open your browser and go to: http://localhost:5000
echo    2. Configure your Jira connection settings
echo    3. Upload your Excel/CSV requirements file
echo    4. Click "Create Jira Tickets" to process
echo.
echo 💡 Tips:
echo    - Make sure your Jira API token has proper permissions
echo    - Supported file formats: .xlsx, .xls, .csv
echo    - Check the console for detailed logs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the Flask server
python api_standalone.py

echo.
echo 👋 Server stopped. Press any key to exit...
pause >nul
