# 🚀 Peak3 Requirements Automation - Startup Guide

## Quick Start

### Option 1: Double-Click to Start
1. **Double-click** `start_peak3_demo.bat` (Windows)
2. **Double-click** `start_peak3_demo.ps1` (PowerShell)
3. **Double-click** `quick_start.bat` (Simple version)

### Option 2: Command Line
```bash
# Navigate to project directory
cd C:\Users\Myxma\OneDrive\Desktop\Peak3_Capstone

# Start the demo
python api_standalone.py
```

## 🌐 Access the Demo

Once started, open your browser and go to:
**http://localhost:5000**

## 📋 Usage Instructions

### 1. Configure Jira Connection
- **Jira Base URL**: `https://yourcompany.atlassian.net`
- **Email**: Your Jira email address
- **API Token**: Your Jira API token (starts with `ATATT3x...`)
- **Project Key**: Your Jira project key (e.g., `PEAK3`, `REQ`)

### 2. Upload Requirements File
- Supported formats: `.xlsx`, `.xls`, `.csv`
- File should contain columns: Requirement ID, Requirement, Description, Priority, Domain, Sub-domain, Requirement type

### 3. Process File
- Click **"Validate File"** to check format
- Click **"Create Jira Tickets"** to create Jira issues

## 🔧 Troubleshooting

### Python Not Found
```bash
# Install Python 3.8+ from https://python.org
# Make sure to check "Add Python to PATH" during installation
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Port Already in Use
```bash
# If port 5000 is busy, modify api_standalone.py line 396:
app.run(debug=True, host='0.0.0.0', port=5001)  # Change to 5001
```

### Jira Connection Issues
1. **Check API Token**: Make sure it's valid and not expired
2. **Check Permissions**: Ensure you have "Create Issues" permission
3. **Check Project Key**: Verify the project exists and you have access
4. **Check Base URL**: Make sure it's the correct Jira instance URL

## 📊 Expected File Format

Your Excel/CSV file should have these columns:
- **Requirement ID**: Unique identifier (e.g., `TRAVEL-CMU-PC-024`)
- **Requirement**: Short requirement title
- **Description**: Detailed requirement description
- **Priority**: P0 (Highest), P1 (High), P2 (Medium), P3 (Low), P4 (Lowest)
- **Domain**: Business domain (e.g., `D2C Quote & Buy journey`)
- **Sub-domain**: Sub-category
- **Requirement type**: Type of requirement

## 🎯 Features

- ✅ **File Validation**: Check file format before processing
- ✅ **Dual Processing**: Choose between Python backend or Forge logic
- ✅ **Jira Integration**: Create Epics and Stories automatically
- ✅ **Error Handling**: Detailed error messages and logging
- ✅ **Real-time Status**: Live updates during processing

## 📞 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify your Jira configuration
3. Ensure file format matches requirements
4. Check network connectivity to Jira

## 🔄 Restart Instructions

To restart the demo:
1. Press `Ctrl+C` in the console to stop the server
2. Run the startup script again
3. Refresh your browser page
