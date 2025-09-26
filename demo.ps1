# Peak3 AI-Powered Requirements Automation Demo Script
# 演示脚本 - 客户展示用

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   Peak3 AI-Powered Requirements Automation   " -ForegroundColor Cyan
Write-Host "           Demo Script v1.0                   " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# 检查环境
Write-Host "1. 环境检查..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   Python版本: $pythonVersion" -ForegroundColor Green
    
    $pandasCheck = python -c "import pandas; print('pandas版本:', pandas.__version__)" 2>&1
    Write-Host "   $pandasCheck" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python环境检查失败" -ForegroundColor Red
    exit 1
}

# 检查配置文件
Write-Host ""
Write-Host "2. 配置文件检查..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   ✅ .env 配置文件存在" -ForegroundColor Green
} else {
    Write-Host "   ❌ .env 配置文件缺失" -ForegroundColor Red
    Write-Host "   请复制 .env.example 为 .env 并填入Jira凭证" -ForegroundColor Yellow
    exit 1
}

if (Test-Path "config.yml") {
    Write-Host "   ✅ config.yml 配置文件存在" -ForegroundColor Green
} else {
    Write-Host "   ❌ config.yml 配置文件缺失" -ForegroundColor Red
    Write-Host "   请复制 config.example.yml 为 config.yml" -ForegroundColor Yellow
    exit 1
}

# 检查示例数据
Write-Host ""
Write-Host "3. 示例数据检查..." -ForegroundColor Yellow
if (Test-Path "sample_requirements.csv") {
    Write-Host "   ✅ 示例数据文件存在" -ForegroundColor Green
    $lineCount = (Get-Content "sample_requirements.csv" | Measure-Object -Line).Lines
    Write-Host "   数据行数: $lineCount" -ForegroundColor Green
} else {
    Write-Host "   ❌ 示例数据文件缺失" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "4. Dry-run 预览（不创建实际工单）..." -ForegroundColor Yellow
Write-Host "   正在分析需求数据并预览将要创建的Epic和Stories..." -ForegroundColor Gray
Write-Host ""

try {
    python -m src.convert -ExcelPath ".\sample_requirements.csv" -ConfigPath ".\config.yml" -DryRun
    Write-Host ""
    Write-Host "   ✅ Dry-run 完成" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Dry-run 失败" -ForegroundColor Red
    Write-Host "   错误信息: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "5. 创建真实Jira工单..." -ForegroundColor Yellow
Write-Host "   正在连接Jira并创建Epic和Stories..." -ForegroundColor Gray
Write-Host ""

try {
    python -m src.convert -ExcelPath ".\sample_requirements.csv" -ConfigPath ".\config.yml"
    Write-Host ""
    Write-Host "   ✅ Jira工单创建完成" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Jira工单创建失败" -ForegroundColor Red
    Write-Host "   错误信息: $_" -ForegroundColor Red
    Write-Host "   请检查Jira凭证和网络连接" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "6. 验证创建结果..." -ForegroundColor Yellow
Write-Host "   正在查询Jira中的最新工单..." -ForegroundColor Gray
Write-Host ""

try {
    $jiraCheck = python -c "
import os, requests
from dotenv import load_dotenv
load_dotenv()
base = os.getenv('JIRA_BASE_URL').rstrip('/')
email = os.getenv('JIRA_EMAIL')
token = os.getenv('JIRA_API_TOKEN')
key = os.getenv('JIRA_PROJECT_KEY')
r = requests.get(f'{base}/rest/api/3/search?jql=project={key} ORDER BY created DESC', auth=(email, token), headers={'Accept':'application/json'})
issues = r.json().get('issues', [])
print('最新创建的工单:')
for i in issues[:8]:
    parent = i['fields'].get('parent', {}).get('key', 'None')
    print(f'  {i[\"key\"]}: {i[\"fields\"][\"summary\"]} ({i[\"fields\"][\"issuetype\"][\"name\"]}) - Parent: {parent}')
"
    Write-Host $jiraCheck -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ 无法查询Jira工单（可能网络问题）" -ForegroundColor Yellow
    Write-Host "   但工单可能已成功创建，请手动检查Jira" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "            Demo 演示完成！                    " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "演示要点总结:" -ForegroundColor Yellow
Write-Host "• Excel需求清单 → Jira Epic/Story 自动转换" -ForegroundColor White
Write-Host "• 智能分组：按Requirement列创建Epic" -ForegroundColor White
Write-Host "• 幂等性：重复运行不会创建重复工单" -ForegroundColor White
Write-Host "• 企业级安全：环境变量管理敏感凭证" -ForegroundColor White
Write-Host "• 时间节省：2小时手工工作 → 5分钟自动化" -ForegroundColor White
Write-Host ""
Write-Host "项目GitHub: https://github.com/yaxuanm/Peak3_Capstone" -ForegroundColor Blue
Write-Host ""
