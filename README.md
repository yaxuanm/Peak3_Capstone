# Peak3 Capstone: AI-Powered Requirements Workflow Automation

Automated conversion of Excel Requirement Lists to Business Specification Documents (BSDs) and Jira Epics/Stories for Peak3 insurance company, leveraging RAG-enhanced content generation with LLMs.

## Features

- **Excel/CSV Ingestion**: Reads both `.xlsx/.xlsm` and `.csv` files
- **Epic Grouping**: Groups requirements by `Requirement` column value
- **Jira Integration**: Creates Epics and Stories with proper hierarchy
- **RAG-Enhanced Content Generation**: Uses Retrieval-Augmented Generation (RAG) with LLMs to generate standardized BSD content aligned with enterprise templates
- **Team-managed Support**: Uses `parent` field for Epic-Story linking
- **Idempotency**: Prevents duplicate creation with search-before-create
- **Dry-run Mode**: Preview changes without creating actual tickets

## Quick Start

### 1. Setup Environment

```powershell
# Clone and navigate to project
git clone <your-repo-url>
cd Peak3_Capstone

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials

```powershell
# Copy example files
copy .env.example .env
copy config.example.yml config.yml

# Edit .env with your Jira credentials
notepad .env
```

Required `.env` values:
```
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=your@email.com
JIRA_API_TOKEN=your_api_token
JIRA_PROJECT_KEY=YOUR_PROJECT_KEY
```

### 3. Configure Column Mapping

Edit `config.yml` to match your Excel column names:

```yaml
excel:
  sheet_name: "1. Requirements - Internal"
  columns:
    requirement_id: "Requirement ID"
    requirement: "Requirement"  # Epic name
    description: "Description"
    priority: "Priority"
    domain: "Domain"
    sub_domain: "Sub-domain"
    requirement_type: "Requirement type"

jira:
  project_key: "YOUR_PROJECT_KEY"
  priority_mapping:
    "P0": "Highest"
    "P1": "High"
    "P2": "Medium"
    "P3": "Low"
    "P4": "Lowest"
```

### 4. Run Conversion

```powershell
# Dry-run (preview only)
python -m src.convert -ExcelPath ".\sample_requirements.csv" -ConfigPath ".\config.yml" -DryRun

# Create actual Jira tickets
python -m src.convert -ExcelPath ".\sample_requirements.csv" -ConfigPath ".\config.yml"
```

## How It Works

1. **Parse Excel**: Reads requirement data and maps columns
2. **Group by Epic**: Groups rows by `Requirement` column value
3. **Create Epic**: Creates one Epic per unique requirement group
4. **Create Stories**: Creates one Story per row, linked to its Epic
5. **Idempotency**: Skips existing Epics/Stories to prevent duplicates

## Story Format

- **Summary**: `[Requirement ID] + first 10 words of description`
- **Description**: Full description in Atlassian Document Format (ADF)
- **Priority**: Mapped from Excel priority (P0-P4 → Jira priorities)
- **Parent**: Linked to corresponding Epic (Team-managed projects)

## Project Structure

```
src/
├── convert.py          # Main conversion logic
├── excel_parser.py     # Excel/CSV parsing
├── jira_client.py      # Jira API integration
├── mappings.py         # Field mapping utilities
└── utils.py           # Common utilities
```

## Troubleshooting

### Common Issues

1. **400 Bad Request**: Check Jira credentials and project permissions
2. **Epic Link errors**: Project uses Team-managed mode (parent field), not Epic Link
3. **Duplicate Epics**: Run with existing data - script will reuse existing Epics

### Getting Jira Credentials

1. **API Token**: https://id.atlassian.com/manage-profile/security/api-tokens
2. **Project Key**: Found in project URL or settings
3. **Base URL**: Your Jira instance URL (e.g., `https://company.atlassian.net`)

## Development

### Adding New Features

- **LLM Integration**: Enhance summary generation with AI
- **RAG-Enhanced Content Generation**: Use Retrieval-Augmented Generation (RAG) with LLMs to generate standardized BSD content aligned with enterprise templates
- **Label Mapping**: Map Domain/Sub-domain to Jira labels
- **Component Mapping**: Map Domain to Jira components
- **Epic Description**: AI-summarized descriptions from grouped requirements

### Testing

```powershell
# Test with sample data
python -m src.convert -ExcelPath ".\sample_requirements.csv" -ConfigPath ".\config.yml" -DryRun
```

## Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## License

Internal project for Peak3 Capstone collaboration.