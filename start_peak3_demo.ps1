# Peak3 Requirements Automation Demo - PowerShell Startup Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Peak3 Requirements Automation Demo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if required packages are installed
Write-Host "🔍 Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import flask, flask_cors, requests, pandas, openpyxl, pyyaml" 2>$null
    Write-Host "✅ All dependencies are available" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Some dependencies are missing. Installing..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "🚀 Starting Peak3 Requirements Automation Demo..." -ForegroundColor Green
Write-Host ""
Write-Host "📋 Instructions:" -ForegroundColor Cyan
Write-Host "   1. Open your browser and go to: http://localhost:5000" -ForegroundColor White
Write-Host "   2. Configure your Jira connection settings" -ForegroundColor White
Write-Host "   3. Upload your Excel/CSV requirements file" -ForegroundColor White
Write-Host "   4. Click 'Create Jira Tickets' to process" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Cyan
Write-Host "   - Make sure your Jira API token has proper permissions" -ForegroundColor White
Write-Host "   - Supported file formats: .xlsx, .xls, .csv" -ForegroundColor White
Write-Host "   - Check the console for detailed logs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start the Flask server
try {
    python api_standalone.py
} catch {
    Write-Host "❌ Failed to start server" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "👋 Server stopped. Press Enter to exit..." -ForegroundColor Yellow
Read-Host
