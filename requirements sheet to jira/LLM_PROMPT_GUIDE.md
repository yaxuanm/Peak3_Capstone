# LLM Prompt Editing Guide

## Overview

Peak3 Requirements Automation uses OpenAI API for data quality checking and intelligent content generation. This guide explains how to edit and customize LLM prompts to meet specific requirements.

## Prompt Locations

LLM prompts are primarily located in the following files:

### 1. Data Quality Check Prompt
**File Location**: `src/data_quality_checker.py`  
**Method**: `data_quality_check()`  
**Line Numbers**: Approximately 80-120 lines

### 2. Content Generation Prompt
**File Location**: `src/data_quality_checker.py`  
**Method**: `_generate_llm_response()`  
**Line Numbers**: Approximately 200-300 lines

## Editing Steps

### Step 1: Locate the Prompt
Open the `src/data_quality_checker.py` file and find the following method:

```python
def data_quality_check(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
    # Find the main prompt here
    prompt = f"""
    You are a data quality checker for requirements management.
    
    [Main prompt content here]
    """
```

### Step 2: Modify the Prompt
Modify the text content in the `prompt` variable. Main modification areas include:

#### 2.1 Role Definition
```python
# Current role definition
"You are a data quality checker for requirements management."

# Can be modified to
"You are an expert business analyst specializing in requirements validation."
```

#### 2.2 Task Description
```python
# Current task description
"Check if the row has all **mandatory Jira mapping fields**:"

# Can be modified to
"Analyze each requirement row for completeness and quality:"
```

#### 2.3 Validation Rules
```python
# Current validation rules
"- Requirement ID  
- Requirement (short title)  
- Description (full text)  
- Priority  
- Domain  
- Epic Link"

# Can add or modify rules
"- Requirement ID (must be unique)
- Requirement (short title, min 10 chars)
- Description (full text, min 50 chars)
- Priority (P0-P4 format)
- Domain (business domain)
- Epic Link (optional but recommended)"
```

#### 2.4 Output Format
```python
# Current output format requirement
"generate a **short Jira summary**:"

# Can be modified to
"generate a **detailed Jira summary with acceptance criteria**:"
```

### Step 3: Test Modifications
After making modifications, test the new prompt:

1. Start the application: `python api_standalone.py`
2. Upload a test file
3. View data validation results
4. Check if LLM-generated content meets expectations

## Common Modification Examples

### Example 1: Modify Validation Strictness
```python
# Original prompt
"If all are present → generate a **short Jira summary**:"

# Modified for stricter validation
"If all are present AND data quality score > 80% → generate a **detailed Jira summary**:"
```

### Example 2: Add New Validation Rules
```python
# Add to validation rules
"- Business Value (must be specified)
- Effort Estimation (must be provided)
- Dependencies (list any dependencies)"
```

### Example 3: Modify Output Format
```python
# Original output format
"Summary = [Requirement ID] + Title"

# Modified to more detailed format
"Summary = [Requirement ID] + [Priority] + Title
Description = As a [user], I want [feature], so that [goal]
Acceptance Criteria = [list of criteria]"
```

### Example 4: Add Business-Specific Rules
```python
# Add rules specific to travel insurance business
"- Coverage Type (must be specified for insurance requirements)
- Risk Level (must be assessed)
- Regulatory Compliance (must be verified)"
```

## Advanced Customization

### 1. Dynamic Prompt Generation
Generate prompts dynamically based on data characteristics:

```python
def generate_dynamic_prompt(self, df: pd.DataFrame) -> str:
    # Analyze data characteristics
    has_priority = 'Priority' in df.columns
    has_domain = 'Domain' in df.columns
    
    # Generate different prompts based on characteristics
    if has_priority and has_domain:
        return self._generate_full_prompt()
    else:
        return self._generate_basic_prompt()
```

### 2. Multi-language Support
Add multi-language prompts:

```python
def get_prompt_by_language(self, language: str = 'en') -> str:
    prompts = {
        'en': self._get_english_prompt(),
        'zh': self._get_chinese_prompt(),
        'es': self._get_spanish_prompt()
    }
    return prompts.get(language, self._get_english_prompt())
```

### 3. Industry-Specific Prompts
Create specialized prompts for different industries:

```python
def get_industry_prompt(self, industry: str) -> str:
    industry_prompts = {
        'insurance': self._get_insurance_prompt(),
        'banking': self._get_banking_prompt(),
        'healthcare': self._get_healthcare_prompt()
    }
    return industry_prompts.get(industry, self._get_default_prompt())
```

## Best Practices

### 1. Prompt Design Principles
- **Clarity**: Instructions should be clear and explicit
- **Specificity**: Provide concrete examples and formats
- **Consistency**: Maintain consistent output format
- **Testability**: Design verifiable outputs

### 2. Testing Strategy
- Use different test datasets
- Validate edge cases
- Check output quality
- Monitor API call costs

### 3. Version Control
- Create version numbers for prompts
- Record modification history
- Keep backup versions
- Test new versions before deployment

## Troubleshooting

### Common Issues

#### 1. LLM Returns Incorrect Format
**Cause**: Prompt instructions are not clear enough
**Solution**: Add specific output format examples in the prompt

#### 2. Validation Too Strict or Too Loose
**Cause**: Validation rules are not properly set
**Solution**: Adjust validation conditions and thresholds

#### 3. Generated Content Quality is Low
**Cause**: Prompt lacks contextual information
**Solution**: Add more business background and examples

#### 4. API Call Fails
**Cause**: Prompt is too long or has format issues
**Solution**: Check prompt length and format

### Debugging Tips

1. **Add Debug Information**:
```python
print(f"Generated prompt: {prompt}")
print(f"LLM response: {response}")
```

2. **Test Small Samples**:
```python
# Process only first 5 rows for testing
test_df = df.head(5)
result = self.data_quality_check(test_df)
```

3. **Compare Different Prompts**:
```python
# Test multiple prompt versions simultaneously
results = []
for prompt_version in prompt_versions:
    result = self.test_prompt(prompt_version, test_data)
    results.append(result)
```

## Configuration Options

Add LLM-related configuration in `config.yml`:

```yaml
llm:
  model: "gpt-3.5-turbo"  # or "gpt-4"
  temperature: 0.3
  max_tokens: 1000
  timeout: 30
  retry_attempts: 3
  
prompt:
  language: "en"  # or "zh", "es"
  industry: "insurance"  # or "banking", "healthcare"
  strict_mode: true  # Strict validation mode
  include_examples: true  # Include examples
```

## Summary

By modifying the prompts in `src/data_quality_checker.py`, you can:

1. Adjust data validation rules
2. Modify output formats
3. Add business-specific logic
4. Optimize content generation quality

Remember to test thoroughly after modifications to ensure the new prompt produces expected results.
