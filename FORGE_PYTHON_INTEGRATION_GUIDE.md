# Forge前端 + Python后端集成指南

## 🎯 集成架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Jira界面      │    │   Forge前端     │    │   Python后端    │
│                 │    │                 │    │                 │
│ 用户上传文件    │───▶│ 调用Python API  │───▶│ 处理业务逻辑    │
│ 配置Jira信息    │    │ 显示处理结果    │    │ 创建Jira工单    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 您需要做的事情

### 1. 部署Python后端供外部访问

#### 选项A: 本地测试 (使用ngrok)
```bash
# 1. 安装ngrok
# 下载: https://ngrok.com/download

# 2. 启动您的Python后端
python api_standalone.py

# 3. 在另一个终端运行ngrok
ngrok http 5000

# 4. 复制ngrok提供的HTTPS地址，例如:
# https://abc123.ngrok.io
```

#### 选项B: 云服务器部署
```bash
# 部署到云服务器 (AWS, Azure, GCP等)
# 确保服务器有公网IP和HTTPS证书
```

### 2. 更新Forge配置

#### 修改Python后端地址
在以下文件中替换 `https://your-python-backend.com` 为您的实际地址:

**文件1: `frontend_temp/src/functions/resolver.ts`**
```typescript
// 第6行，替换为您的实际地址
const PYTHON_BACKEND_URL = 'https://your-actual-backend.com/api';
```

**文件2: `frontend_temp/manifest.yml`**
```yaml
# 第43行和第50行，替换为您的实际地址
- address: https://your-actual-backend.com
```

### 3. 部署Forge应用

```bash
# 进入Forge前端目录
cd frontend_temp

# 安装依赖
npm install

# 构建应用
npm run build

# 部署到Forge平台
npm run deploy

# 安装到Jira
npm run install-app
```

## 🔧 配置步骤详解

### 步骤1: 获取Python后端地址

**如果您使用ngrok:**
```bash
# 运行ngrok后，会显示类似这样的信息:
# Forwarding  https://abc123.ngrok.io -> http://localhost:5000
# 使用: https://abc123.ngrok.io
```

**如果您使用云服务器:**
```bash
# 确保您的服务器地址是HTTPS
# 例如: https://your-server.com
```

### 步骤2: 更新配置文件

**更新resolver.ts:**
```typescript
// 将第6行改为您的实际地址
const PYTHON_BACKEND_URL = 'https://abc123.ngrok.io/api';
```

**更新manifest.yml:**
```yaml
permissions:
  external:
    fetch:
      client:
        - address: https://abc123.ngrok.io  # 您的实际地址
      backend:
        - address: https://abc123.ngrok.io  # 您的实际地址
```

### 步骤3: 测试集成

1. **启动Python后端:**
   ```bash
   python api_standalone.py
   ```

2. **启动ngrok (如果使用):**
   ```bash
   ngrok http 5000
   ```

3. **部署Forge应用:**
   ```bash
   cd frontend_temp
   npm run deploy
   npm run install-app
   ```

4. **在Jira中测试:**
   - 进入任何Jira项目
   - 在左侧菜单找到"Peak3 Requirements Automation"
   - 上传Excel文件测试

## 🚨 注意事项

### 1. HTTPS要求
- Forge要求所有外部API调用必须使用HTTPS
- 本地测试必须使用ngrok或类似工具
- 生产环境需要有效的SSL证书

### 2. 权限配置
- 已移除`manage:jira-project`权限以避免Premium要求
- 如果您的Python后端需要创建项目，请在Python代码中处理

### 3. 错误处理
- Forge前端会显示Python后端的错误信息
- 检查浏览器控制台和Forge日志获取详细错误

## 🧪 测试清单

- [ ] Python后端可以外部访问 (HTTPS)
- [ ] Forge配置已更新为正确的后端地址
- [ ] Forge应用已成功部署
- [ ] 在Jira中可以看到"Peak3 Requirements Automation"
- [ ] 可以上传Excel文件
- [ ] 可以配置Jira连接信息
- [ ] 可以成功创建Jira工单

## 🔍 故障排除

### 常见问题

1. **"Python backend error: 404"**
   - 检查Python后端地址是否正确
   - 确保Python后端正在运行

2. **"Forge app not showing in Jira"**
   - 检查Forge应用是否成功安装
   - 检查用户权限

3. **"External fetch not allowed"**
   - 检查manifest.yml中的external.fetch配置
   - 确保地址格式正确

### 调试方法

1. **查看Forge日志:**
   ```bash
   forge logs
   ```

2. **查看Python后端日志:**
   - 检查控制台输出
   - 检查错误信息

3. **查看浏览器控制台:**
   - 打开Jira页面
   - 按F12打开开发者工具
   - 查看Console和Network标签

## 🎉 完成后的效果

- ✅ 用户在Jira界面中直接使用
- ✅ 无需离开Jira环境
- ✅ 调用您的Python后端处理业务逻辑
- ✅ 在Jira中创建Epic和Story
- ✅ 无需Jira Premium订阅
- ✅ 完全集成到Jira工作流

---

**需要帮助？** 如果在任何步骤遇到问题，请告诉我具体的错误信息！
