# Peak3 Requirements Automation - 快速启动指南

## 🚀 5分钟快速开始

### 步骤1: 环境准备
确保您的系统已安装：
- Python 3.8 或更高版本
- pip 包管理器

### 步骤2: 下载项目
```bash
git clone <repository-url>
cd Peak3_Capstone
```

### 步骤3: 安装依赖
```bash
pip install -r requirements.txt
```

### 步骤4: 配置环境变量
创建 `.env` 文件：
```bash
# 复制示例文件
cp .env.example .env

# 编辑配置文件
# 在 .env 文件中添加您的API密钥
```

编辑 `.env` 文件，添加以下内容：
```env
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token
OPENAI_API_KEY=your-openai-api-key
```

### 步骤5: 启动应用
```bash
python api_standalone.py
```

### 步骤6: 访问应用
打开浏览器访问：http://localhost:5000

## 📋 测试流程

### 1. 使用示例数据测试
1. 访问 http://localhost:5000
2. 点击 "Choose File" 按钮
3. 选择 `data/sample_requirements.csv` 文件
4. 配置Jira设置（使用您的Jira信息）
5. 点击 "Validate File" 查看验证结果和AI生成的摘要
6. 点击 "Create Jira Tickets" 创建票据（包含LLM增强的描述）
7. 使用导出功能下载结果

### 2. 使用自己的数据测试
1. 准备Excel或CSV格式的需求文档
2. 确保包含以下列：
   - Requirement ID
   - Requirement
   - Description
   - Priority
   - Domain
3. 按照上述流程上传和处理

## 🔧 配置说明

### Jira配置
- **Base URL**: 您的Jira实例地址
- **Email**: Jira账户邮箱
- **API Token**: 在Jira中生成的API令牌
- **Project Key**: 目标项目的Key（如SCRUM）

### 文件格式要求
CSV文件应包含以下列：
```
Requirement ID,Requirement,Description,Priority,Domain,Sub-domain
TRAVEL-CMU-PC-024,1 - D2C Quote & Buy journey,The CMU Travel Insurance...,P2,2 - Policy Issuance,3 - Sales
```

## 🐛 常见问题

### 问题1: 无法启动应用
**错误**: `ModuleNotFoundError: No module named 'flask'`
**解决**: 运行 `pip install -r requirements.txt`

### 问题2: Jira连接失败
**错误**: `Jira API Error 401`
**解决**: 检查Jira URL、邮箱和API Token是否正确

### 问题3: 文件上传失败
**错误**: 文件格式不支持
**解决**: 确保文件是Excel (.xlsx) 或CSV (.csv) 格式

### 问题4: 数据验证失败
**错误**: 验证结果显示错误
**解决**: 检查数据是否包含必填字段，格式是否正确

## 📊 示例数据说明

项目包含完整的示例数据文件 `data/sample_requirements.csv`：

- **记录数量**: 21条需求记录
- **业务领域**: 旅行保险业务
- **数据完整性**: 包含所有必填字段
- **优先级范围**: P0-P4
- **功能覆盖**: 涵盖完整的业务流程

## 🎯 功能验证清单

### 基础功能
- [ ] 文件上传成功
- [ ] 数据验证通过
- [ ] Jira连接正常
- [ ] 票据创建成功
- [ ] 导出功能正常

### 高级功能
- [ ] 数据质量检查
- [ ] 智能内容生成
- [ ] 错误处理机制
- [ ] 用户界面响应

## 📞 获取帮助

如果遇到问题：

1. **查看日志**: 控制台会显示详细的错误信息
2. **检查配置**: 确认所有配置项都正确设置
3. **测试连接**: 验证Jira和OpenAI API连接
4. **查看文档**: 参考完整的README.md文档

## 🔄 下一步

成功启动后，您可以：

1. **自定义配置**: 修改 `config.yml` 文件
2. **调整Prompt**: 编辑LLM prompt（参考LLM_PROMPT_GUIDE.md）
3. **扩展功能**: 根据需求添加新功能
4. **部署生产**: 配置生产环境部署

---

**恭喜！** 您已成功启动Peak3 Requirements Automation系统！🎉
