# 🚀 Peak3 Forge应用部署指南

**收件人**: 团队成员  
**发件人**: [您的姓名]  
**日期**: 2025年10月16日  
**优先级**: 高

---

## 📋 部署任务概述

Peak3需求自动化系统的Forge前端已准备就绪，需要手动部署到Atlassian Forge平台。后端服务已在AWS EC2上运行，所有配置已完成。

## ✅ 当前状态

### 后端服务
- **状态**: ✅ 运行正常
- **地址**: `http://54.242.32.81:8080`
- **所有API端点**: 测试通过
- **安全组**: 已配置

### 前端代码
- **状态**: ✅ 开发完成
- **位置**: `frontend_temp/peak3_demo/`
- **配置**: 已指向EC2后端
- **构建**: 成功

## 🎯 部署步骤

### 1. 环境准备
```bash
# 确保Node.js版本 (推荐20.x或22.x)
node --version

# 安装Forge CLI (如果未安装)
npm install -g @forge/cli
```

### 2. 进入项目目录
```bash
cd frontend_temp/peak3_demo
```

### 3. 安装依赖
```bash
npm install
```

### 4. 构建项目
```bash
npm run build
```

### 5. 登录Forge CLI
```bash
forge login
```
**注意**: 这会打开浏览器，需要：
- 登录您的Atlassian账户
- 授权Forge CLI访问权限
- 获取API Token

### 6. 部署应用
```bash
forge deploy
```

### 7. 安装到Jira
```bash
forge install
```
**注意**: 需要选择目标Jira站点

## 🔧 配置验证

### 检查manifest.yml配置
确保以下配置正确：
```yaml
permissions:
  external:
    fetch:
      client:
        - address: http://54.242.32.81:8080
      backend:
        - address: http://54.242.32.81:8080
```

### 检查resolver.ts配置
确保API地址正确：
```typescript
const PYTHON_BACKEND_URL = 'http://54.242.32.81:8080/api';
```

## 🧪 部署后测试

### 1. 在Jira中打开应用
- 进入Jira项目页面
- 查找"Peak3 Requirements Automation"应用
- 点击打开

### 2. 测试文件上传
使用提供的测试文件：`sample_requirements.csv`

### 3. 验证功能
- ✅ 文件上传成功
- ✅ 文件解析正常
- ✅ 数据验证通过
- ✅ Jira工单创建成功

## 📊 测试数据格式

### sample_requirements.csv内容
```csv
Requirement ID,Requirement type,Sales product,Tenant/Partner,Domain,Sub-domain,Requirement,Description,Priority
REQ-001,Functional,Product A,Partner 1,Authentication,Login,User Login,User should be able to login with credentials,P1
REQ-002,Functional,Product A,Partner 1,Authentication,Password,Password Reset,User should be able to reset password,P2
```

## 🚨 可能遇到的问题

### 1. Forge登录失败
**解决方案**:
```bash
# 使用环境变量
export FORGE_API_TOKEN="your_api_token"
export FORGE_ACCOUNT_ID="your_account_id"
forge deploy
```

### 2. 部署权限错误
**解决方案**:
- 确保Atlassian账户有Forge应用开发权限
- 检查API Token权限设置

### 3. 后端连接失败
**解决方案**:
- 测试后端连接: `curl http://54.242.32.81:8080/api/health`
- 检查网络连接
- 验证安全组配置

### 4. 文件解析错误
**解决方案**:
- 检查Excel文件格式
- 确保列名匹配配置
- 查看Forge应用日志

## 📞 技术支持

### 如果遇到问题
1. **检查日志**: 查看Forge应用日志
2. **测试后端**: 验证EC2服务状态
3. **联系支持**: 及时反馈问题

### 联系信息
- **技术负责人**: [您的姓名]
- **部署时间**: 2025-10-16
- **紧急联系**: [您的联系方式]

## 📋 部署检查清单

- [ ] Node.js环境准备
- [ ] Forge CLI安装
- [ ] 项目依赖安装
- [ ] 项目构建成功
- [ ] Forge CLI登录
- [ ] 应用部署成功
- [ ] 应用安装到Jira
- [ ] 功能测试通过
- [ ] 文件上传测试
- [ ] Jira工单创建测试

## 🎉 部署成功标志

当您看到以下信息时，表示部署成功：
- ✅ `forge deploy` 显示成功消息
- ✅ `forge install` 完成安装
- ✅ 在Jira中可以看到应用
- ✅ 可以成功上传和处理文件
- ✅ 可以创建Jira工单

## 📈 后续步骤

部署成功后：
1. **用户培训**: 向团队介绍应用使用方法
2. **文档更新**: 更新用户手册
3. **监控设置**: 设置应用监控
4. **反馈收集**: 收集用户反馈

---

**重要提醒**: 
- 部署过程中如遇到任何问题，请立即联系技术团队
- 建议在测试环境先验证，再部署到生产环境
- 部署完成后请进行完整的功能测试

**预计部署时间**: 30-45分钟  
**部署复杂度**: 中等  
**风险等级**: 低

---

**祝部署顺利！** 🚀

