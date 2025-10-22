# Peak3 Requirements Automation System

## 🎯 Project Overview

Peak3 Requirements Automation System is a complete solution for automatically converting Excel/CSV requirement files to Jira tickets. The system uses a frontend-backend separation architecture, with the frontend built on Atlassian Forge platform and the backend deployed on AWS EC2.

## 🏗️ System Architecture

### Key Features
- **Excel/CSV Ingestion**: Reads both `.xlsx/.xlsm` and `.csv` files
- **AI-Powered Data Quality Check**: Validates data completeness and quality before Jira mapping
- **Epic Grouping**: Groups requirements by `Requirement` column value
- **Jira Integration**: Creates Epics and Stories with proper hierarchy
- **Team-managed Support**: Uses `parent` field for Epic-Story linking
- **Idempotency**: Prevents duplicate creation with search-before-create
- **Dry-run Mode**: Preview changes without creating actual tickets

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Forge Frontend│    │   EC2 Backend   │    │   Jira Cloud    │
│   (Jira Integration)│───▶│   (Python API)  │───▶│   (Ticket Creation)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack
- **Frontend**: Atlassian Forge (TypeScript, HTML, CSS)
- **Backend**: Python Flask (REST API)
- **Deployment**: AWS EC2
- **Integration**: Jira Cloud API

## 🚀 Quick Start

### Prerequisites
- Node.js 20.x or 22.x
- Python 3.9+
- Atlassian Account
- AWS Account

### 1. Backend Service Status
Backend service is deployed on AWS EC2:
- **Service URL**: `http://54.242.32.81:8080`
- **Status**: ✅ Running normally
- **API Endpoints**:
  - Health Check: `/api/health`
  - File Validation: `/api/validate`
  - File Processing: `/api/process`
  - Forge Integration: `/api/forge/process`

### 2. Frontend Deployment
```bash
# Navigate to Forge project directory
cd frontend_temp/peak3_demo

# Install dependencies
npm install

# Build project
npm run build

# Login to Forge CLI
forge login

# Deploy application
forge deploy

# Install to Jira
forge install
```

## 📁 Project Structure

```
Peak3_Capstone/
├── src/                          # Python backend source code
│   ├── api.py                    # Flask API main file
│   ├── convert.py                # File conversion logic
│   ├── excel_parser.py           # Excel parser
│   ├── jira_client.py            # Jira client
│   ├── forge_integration.py      # Forge integration module
│   └── utils.py                  # Utility functions
├── frontend_temp/peak3_demo/     # Forge frontend project
│   ├── src/
│   │   ├── resolver.ts           # Forge resolver
│   │   ├── parseExcel.ts         # Excel processing
│   │   ├── createJira.ts         # Jira creation
│   │   └── callLLM.ts            # LLM calls
│   ├── static/
│   │   ├── index.html            # Main interface
│   │   └── styles.css            # Style files
│   ├── manifest.yml              # Forge configuration
│   └── package.json              # Dependencies configuration
├── static/                       # Local web interface
├── config.yml                    # Configuration file
├── requirements.txt              # Python dependencies
└── sample_requirements.csv       # Sample data
```

## 🔧 Configuration

### 1. Environment Variables

Required `.env` values:
```
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=your@email.com
JIRA_API_TOKEN=your_api_token
JIRA_PROJECT_KEY=YOUR_PROJECT_KEY
OPENAI_API_KEY=your_openai_api_key
```

### 2. Configure Column Mapping

Edit `config.yml` to match your Excel column names:

### Backend Configuration (config.yml)
```yaml
excel:
  sheet_name: "1. Requirements - Internal"  # Excel worksheet name
  columns:
    requirement_id: "Requirement ID"
    requirement: "Requirement"
    description: "Description"
    priority: "Priority"
    domain: "Domain"
    sub_domain: "Sub-domain"
    requirement_type: "Requirement type"

jira:
  project_key: "SCRUM"
  epic_link_field_key: "customfield_10014"
  priority_mapping:
    "P0": "Highest"
    "P1": "High"
    "P2": "Medium"
    "P3": "Low"
    "P4": "Lowest"

data_quality:
  enabled: true
  openai_model: "gpt-4o-mini"
  max_tokens: 2000
  temperature: 0.3
```

### Forge配置 (manifest.yml)
```yaml
app:
  id: ari:cloud:ecosystem::app/17ebda9a-24a4-4606-8c85-d4c788d780fb
  runtime:
    name: nodejs22.x

<<<<<<< HEAD
permissions:
  scopes:
    - read:jira-work
    - write:jira-work
  external:
    fetch:
      client:
        - address: http://54.242.32.81:8080
      backend:
        - address: http://54.242.32.81:8080
=======
```powershell
# Dry-run (preview only) with Excel file
python -m src.convert -ExcelPath ".\requirements.xlsx" -ConfigPath ".\config.yml" -DryRun

# Create actual Jira tickets from Excel file
python -m src.convert -ExcelPath ".\requirements.xlsx" -ConfigPath ".\config.yml"

# Skip data quality check
python -m src.convert -ExcelPath ".\requirements.xlsx" -ConfigPath ".\config.yml" -SkipQualityCheck
>>>>>>> origin/llm_integrated
```

## 📊 Data Format

<<<<<<< HEAD
### Excel/CSV File Format
Files must contain the following columns:
- **Requirement ID**: Requirement ID
- **Requirement**: Requirement title
- **Description**: Requirement description
- **Priority**: Priority (P0-P4)
- **Domain**: Domain
- **Sub-domain**: Sub-domain
- **Requirement type**: Requirement type
=======
1. **Parse Excel**: Reads requirement data and maps columns
2. **Data Quality Check**: AI-powered validation of data completeness and quality
3. **Group by Epic**: Groups rows by `Requirement` column value
4. **Create Epic**: Creates one Epic per unique requirement group
5. **Create Stories**: Creates one Story per row, linked to its Epic
6. **Idempotency**: Skips existing Epics/Stories to prevent duplicates
>>>>>>> origin/llm_integrated

### Priority Mapping
- P0 → Highest
- P1 → High
- P2 → Medium
- P3 → Low
- P4 → Lowest

## 🧪 Testing

### 1. Backend API Testing
```bash
# Health check
curl http://54.242.32.81:8080/api/health

<<<<<<< HEAD
# File validation
curl -X POST http://54.242.32.81:8080/api/validate \
  -H "Content-Type: application/json" \
  -d '{"fileContent":"base64_content","fileName":"test.csv"}'
=======
```
src/
├── convert.py              # Main conversion logic
├── excel_parser.py         # Excel/CSV parsing
├── jira_client.py          # Jira API integration
├── mappings.py             # Field mapping utilities
├── utils.py               # Common utilities
└── data_quality_checker.py # AI-powered data quality validation
>>>>>>> origin/llm_integrated
```

### 2. Frontend Testing
1. Open the application in Jira
2. Upload `sample_requirements.csv` file
3. Verify file parsing and ticket creation

## 🔍 Troubleshooting

### Common Issues

1. **Forge Login Failed**
   ```bash
   # Use environment variables
   export FORGE_API_TOKEN="your_token"
   export FORGE_ACCOUNT_ID="your_account_id"
   ```

2. **Backend Connection Failed**
   - Check EC2 instance status
   - Verify security group configuration (port 8080)
   - Confirm service running status

3. **File Parsing Error**
   - Check if Excel column names match
   - Verify file format (.xlsx, .xls, .csv)
   - Check backend logs

<<<<<<< HEAD
### Log Viewing
```bash
# EC2 service logs
ssh -i yaxuanm.pem ec2-user@54.242.32.81
cat /home/ec2-user/peak3-backend/app.log
=======
## Development

### Adding New Features

- **LLM Integration**: Enhance summary generation with AI
- **Label Mapping**: Map Domain/Sub-domain to Jira labels
- **Component Mapping**: Map Domain to Jira components
- **Epic Description**: AI-summarized descriptions from grouped requirements

### Testing

```powershell
# Test with sample data (CSV)
python -m src.convert -ExcelPath ".\sample_requirements.csv" -ConfigPath ".\config.yml" -DryRun

# Test with Excel file
python -m src.convert -ExcelPath ".\requirements.xlsx" -ConfigPath ".\config.yml" -DryRun
>>>>>>> origin/llm_integrated
```

## 📈 Features

- ✅ **File Parsing**: Supports Excel and CSV formats
- ✅ **Data Validation**: Automatic data integrity validation
- ✅ **Jira Integration**: Automatic Epic and Story creation
- ✅ **Priority Mapping**: Smart priority conversion
- ✅ **Error Handling**: Comprehensive error handling mechanism
- ✅ **Forge Integration**: Native Jira application experience

## 🔐 Security Configuration

### AWS Security Group
- Port 22 (SSH): Management access
- Port 8080 (HTTP): API access
- Source: 0.0.0.0/0 (can be restricted as needed)

### Jira Permissions
- read:jira-work: Read tickets
- write:jira-work: Create/modify tickets

## 📞 Technical Support

### Contact Information
- **Project Lead**: [Your Name]
- **Deployment Date**: 2025-10-16
- **Service Status**: 🟢 Running normally

### Related Documentation
- AWS Deployment Guide: `AWS_DEPLOYMENT_GUIDE.md`
- Forge Integration Guide: `FORGE_PYTHON_INTEGRATION_GUIDE.md`
- Team Message: `TEAM_MESSAGE.md`

## 🎉 Project Milestones

- ✅ Backend API development completed
- ✅ EC2 deployment successful
- ✅ Forge frontend development completed
- ✅ Frontend-backend integration completed
- ✅ Security configuration completed
- 🔄 **Current Status**: Ready for production deployment

---

**Last Updated**: 2025-10-16  
**Version**: 1.0.0  
**Status**: 🟢 Production Ready