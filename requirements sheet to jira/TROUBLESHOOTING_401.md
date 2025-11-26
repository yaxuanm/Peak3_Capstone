# 解决 Jira API 401 认证错误

## 错误信息
```
HTTP Error 500: { "error": "401 Client Error: Unauthorized for url: https://peak3capstone.atlassian.net/rest/api/3/issue", "success": false }
```

## 问题原因

401 Unauthorized 错误表示 Jira API 认证失败。常见原因包括：

1. **API Token 已过期或无效**
2. **Email 地址不正确**
3. **API Token 格式错误**（可能包含多余的空格或换行）
4. **账户权限不足**（账户可能被禁用或没有API访问权限）

## 解决步骤

### 步骤 1: 验证 API Token

1. 访问 Atlassian 账户管理页面：
   ```
   https://id.atlassian.com/manage-profile/security/api-tokens
   ```

2. 检查现有的 API Token：
   - 如果 Token 已过期，需要创建新的
   - 如果 Token 不存在，需要创建新的

3. 创建新的 API Token：
   - 点击 "Create API token"
   - 输入标签名称（例如："Peak3 Requirements Automation"）
   - 点击 "Create"
   - **立即复制 Token**（只显示一次）

### 步骤 2: 验证 Email 地址

确保使用的 Email 地址是：
- 与 Jira 账户关联的邮箱地址
- 不是别名或转发邮箱
- 在 Jira 中已验证的邮箱

### 步骤 3: 更新配置

#### 方法 1: 通过 Web 界面更新

1. 访问 http://localhost:5000
2. 在 "Configure Jira Connection" 部分更新：
   - **Jira Base URL**: `https://peak3capstone.atlassian.net`
   - **Email Address**: 您的 Jira 邮箱地址
   - **API Token**: 新创建的 API Token（完整复制，无空格）
   - **Project Key**: `SCRUM`（或您的项目Key）

#### 方法 2: 更新代码中的默认值

编辑 `api_standalone.py` 文件，更新第 121-126 行的默认配置：

```python
jira_config = {
    'baseUrl': 'https://peak3capstone.atlassian.net',
    'email': 'your-email@example.com',  # 更新为您的邮箱
    'apiToken': 'YOUR_NEW_API_TOKEN',   # 更新为新创建的Token
    'projectKey': 'SCRUM'
}
```

### 步骤 4: 测试连接

运行测试脚本验证连接：

```bash
cd "requirements sheet to jira"
python test_jira_connection.py
```

或者使用自定义参数：

```bash
python test_jira_connection.py "https://peak3capstone.atlassian.net" "your-email@example.com" "YOUR_API_TOKEN"
```

### 步骤 5: 验证项目权限

确保您的账户有权限访问目标项目：

1. 登录 Jira: https://peak3capstone.atlassian.net
2. 检查项目 "SCRUM" 是否存在
3. 确认您有创建 Issue 的权限

## 常见问题

### Q: API Token 格式是什么？
A: API Token 通常以 `ATATT3x` 开头，长度约为 200+ 字符。确保完整复制，不要截断。

### Q: 可以使用密码代替 API Token 吗？
A: 不可以。Jira Cloud 要求使用 API Token，不能使用账户密码。

### Q: API Token 会过期吗？
A: API Token 不会自动过期，但可以手动撤销。如果遇到认证错误，建议创建新的 Token。

### Q: 如何检查 Token 是否有效？
A: 运行 `test_jira_connection.py` 脚本，如果所有测试通过，说明 Token 有效。

## 仍然无法解决？

如果按照上述步骤操作后仍然遇到 401 错误：

1. **检查网络连接**：确保可以访问 `https://peak3capstone.atlassian.net`
2. **检查账户状态**：登录 Jira 确认账户未被禁用
3. **检查项目权限**：确认有权限在目标项目中创建 Issue
4. **查看详细日志**：检查服务器控制台输出的详细错误信息
5. **联系管理员**：如果账户权限有问题，联系 Jira 管理员

## 相关文件

- `test_jira_connection.py` - 连接测试脚本
- `api_standalone.py` - API 服务器主文件
- `src/jira_client.py` - Jira 客户端实现



