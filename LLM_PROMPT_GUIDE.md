# LLM Prompt 编辑指南

## 概述

Peak3 Requirements Automation 使用OpenAI API进行数据质量检查和智能内容生成。本指南说明如何编辑和自定义LLM prompt以满足特定需求。

## Prompt 位置

LLM prompt 主要位于以下文件中：

### 1. 数据质量检查 Prompt
**文件位置**: `src/data_quality_checker.py`  
**方法**: `data_quality_check()`  
**行数**: 约80-120行

### 2. 内容生成 Prompt
**文件位置**: `src/data_quality_checker.py`  
**方法**: `_generate_llm_response()`  
**行数**: 约200-300行

## 编辑步骤

### 步骤1: 定位Prompt
打开 `src/data_quality_checker.py` 文件，找到以下方法：

```python
def data_quality_check(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
    # 在这里找到主要的prompt
    prompt = f"""
    You are a data quality checker for requirements management.
    
    [这里是主要的prompt内容]
    """
```

### 步骤2: 修改Prompt
在 `prompt` 变量中修改文本内容。主要修改区域包括：

#### 2.1 角色定义
```python
# 当前角色定义
"You are a data quality checker for requirements management."

# 可以修改为
"You are an expert business analyst specializing in requirements validation."
```

#### 2.2 任务描述
```python
# 当前任务描述
"Check if the row has all **mandatory Jira mapping fields**:"

# 可以修改为
"Analyze each requirement row for completeness and quality:"
```

#### 2.3 验证规则
```python
# 当前验证规则
"- Requirement ID  
- Requirement (short title)  
- Description (full text)  
- Priority  
- Domain  
- Epic Link"

# 可以添加或修改规则
"- Requirement ID (must be unique)
- Requirement (short title, min 10 chars)
- Description (full text, min 50 chars)
- Priority (P0-P4 format)
- Domain (business domain)
- Epic Link (optional but recommended)"
```

#### 2.4 输出格式
```python
# 当前输出格式要求
"generate a **short Jira summary**:"

# 可以修改为
"generate a **detailed Jira summary with acceptance criteria**:"
```

### 步骤3: 测试修改
修改完成后，需要测试新的prompt：

1. 启动应用：`python api_standalone.py`
2. 上传测试文件
3. 查看数据验证结果
4. 检查LLM生成的内容是否符合预期

## 常用修改示例

### 示例1: 修改验证严格程度
```python
# 原始prompt
"If all are present → generate a **short Jira summary**:"

# 修改为更严格的验证
"If all are present AND data quality score > 80% → generate a **detailed Jira summary**:"
```

### 示例2: 添加新的验证规则
```python
# 在验证规则中添加
"- Business Value (must be specified)
- Effort Estimation (must be provided)
- Dependencies (list any dependencies)"
```

### 示例3: 修改输出格式
```python
# 原始输出格式
"Summary = [Requirement ID] + Title"

# 修改为更详细的格式
"Summary = [Requirement ID] + [Priority] + Title
Description = As a [user], I want [feature], so that [goal]
Acceptance Criteria = [list of criteria]"
```

### 示例4: 添加特定业务规则
```python
# 添加特定于旅行保险业务的规则
"- Coverage Type (must be specified for insurance requirements)
- Risk Level (must be assessed)
- Regulatory Compliance (must be verified)"
```

## 高级自定义

### 1. 动态Prompt生成
可以基于数据特征动态生成prompt：

```python
def generate_dynamic_prompt(self, df: pd.DataFrame) -> str:
    # 分析数据特征
    has_priority = 'Priority' in df.columns
    has_domain = 'Domain' in df.columns
    
    # 根据特征生成不同的prompt
    if has_priority and has_domain:
        return self._generate_full_prompt()
    else:
        return self._generate_basic_prompt()
```

### 2. 多语言支持
可以添加多语言prompt：

```python
def get_prompt_by_language(self, language: str = 'en') -> str:
    prompts = {
        'en': self._get_english_prompt(),
        'zh': self._get_chinese_prompt(),
        'es': self._get_spanish_prompt()
    }
    return prompts.get(language, self._get_english_prompt())
```

### 3. 行业特定Prompt
可以为不同行业创建专门的prompt：

```python
def get_industry_prompt(self, industry: str) -> str:
    industry_prompts = {
        'insurance': self._get_insurance_prompt(),
        'banking': self._get_banking_prompt(),
        'healthcare': self._get_healthcare_prompt()
    }
    return industry_prompts.get(industry, self._get_default_prompt())
```

## 最佳实践

### 1. Prompt设计原则
- **明确性**: 指令要清晰明确
- **具体性**: 提供具体的示例和格式
- **一致性**: 保持输出格式的一致性
- **可测试性**: 设计可验证的输出

### 2. 测试策略
- 使用不同的测试数据集
- 验证边界情况
- 检查输出质量
- 监控API调用成本

### 3. 版本控制
- 为prompt创建版本号
- 记录修改历史
- 保留备份版本
- 测试新版本后再部署

## 故障排除

### 常见问题

#### 1. LLM返回格式不正确
**原因**: Prompt指令不够明确
**解决**: 在prompt中添加具体的输出格式示例

#### 2. 验证过于严格或宽松
**原因**: 验证规则设置不当
**解决**: 调整验证条件和阈值

#### 3. 生成内容质量不高
**原因**: Prompt缺乏上下文信息
**解决**: 添加更多业务背景和示例

#### 4. API调用失败
**原因**: Prompt过长或格式问题
**解决**: 检查prompt长度和格式

### 调试技巧

1. **添加调试信息**:
```python
print(f"Generated prompt: {prompt}")
print(f"LLM response: {response}")
```

2. **测试小样本**:
```python
# 只处理前5行数据进行测试
test_df = df.head(5)
result = self.data_quality_check(test_df)
```

3. **比较不同prompt**:
```python
# 同时测试多个prompt版本
results = []
for prompt_version in prompt_versions:
    result = self.test_prompt(prompt_version, test_data)
    results.append(result)
```

## 配置选项

在 `config.yml` 中可以添加LLM相关配置：

```yaml
llm:
  model: "gpt-3.5-turbo"  # 或 "gpt-4"
  temperature: 0.3
  max_tokens: 1000
  timeout: 30
  retry_attempts: 3
  
prompt:
  language: "en"  # 或 "zh", "es"
  industry: "insurance"  # 或 "banking", "healthcare"
  strict_mode: true  # 严格验证模式
  include_examples: true  # 包含示例
```

## 总结

通过修改 `src/data_quality_checker.py` 中的prompt，您可以：

1. 调整数据验证规则
2. 修改输出格式
3. 添加业务特定逻辑
4. 优化内容生成质量

记住在修改后充分测试，确保新的prompt能够产生预期的结果。
