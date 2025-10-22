"""
Forge Frontend Integration - Python implementation of original Forge functions
This module replicates the original Forge frontend logic in Python
"""

import base64
import json
import re
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import requests
try:
    from .utils import coalesce_str
except ImportError:
    from utils import coalesce_str

class ForgeExcelParser:
    """Python implementation of the original Forge parseExcel function"""
    
    DEFAULT_COLUMNS_CFG = {
        'requirement_id': "Requirement ID",
        'requirement': "Requirement", 
        'description': "Description",
        'priority': "Priority",
        'domain': "Domain",
        'subdomain': "Sub-domain",
        'requirement_type': "Requirement type"
    }
    
    def get_file_extension(self, filename: str) -> str:
        """Get file extension from filename"""
        ext = filename.lower().split('.').pop()
        return ext or ''
    
    def is_csv_file(self, filename: str) -> bool:
        """Check if file is CSV/TXT"""
        ext = self.get_file_extension(filename)
        return ext in ['csv', 'txt']
    
    def read_any_table(self, file_content: bytes, filename: str) -> List[Dict[str, Any]]:
        """Read CSV or Excel file and return records"""
        if self.is_csv_file(filename):
            return self._read_csv(file_content)
        else:
            return self._read_excel(file_content)
    
    def _read_csv(self, file_content: bytes) -> List[Dict[str, Any]]:
        """Read CSV file content"""
        try:
            # Try to decode as UTF-8 first
            text = file_content.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback to other encodings
            try:
                text = file_content.decode('latin-1')
            except UnicodeDecodeError:
                text = file_content.decode('utf-8', errors='ignore')
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return []
        
        # Parse CSV headers and data
        headers = [h.strip().strip('"') for h in lines[0].split(',')]
        records = []
        
        for line in lines[1:]:
            values = [v.strip().strip('"') for v in line.split(',')]
            record = {}
            for i, header in enumerate(headers):
                record[header] = values[i] if i < len(values) else ''
            records.append(record)
        
        return records
    
    def _read_excel(self, file_content: bytes) -> List[Dict[str, Any]]:
        """Read Excel file content"""
        import io
        df = pd.read_excel(io.BytesIO(file_content), sheet_name=0)
        return df.to_dict('records')
    
    def normalize_records(self, records: List[Dict[str, Any]], columns_cfg: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """Normalize records using column mapping"""
        if columns_cfg is None:
            columns_cfg = self.DEFAULT_COLUMNS_CFG
        
        normalized = []
        for raw in records:
            normalized.append({
                'requirement_id': coalesce_str(raw.get(columns_cfg['requirement_id'])),
                'requirement': coalesce_str(raw.get(columns_cfg['requirement'])),
                'description': coalesce_str(raw.get(columns_cfg['description'])),
                'priority': coalesce_str(raw.get(columns_cfg['priority'])),
                'domain': coalesce_str(raw.get(columns_cfg['domain'])),
                'subdomain': coalesce_str(raw.get(columns_cfg['subdomain'])),
                'requirement_type': coalesce_str(raw.get(columns_cfg['requirement_type']))
            })
        return normalized
    
    def group_by_epic(self, records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group records by epic name"""
        groups = {}
        for record in records:
            epic_name = record.get('requirement') or "Unnamed Epic"
            if epic_name not in groups:
                groups[epic_name] = []
            groups[epic_name].append(record)
        return groups
    
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Main parsing function - replicates Forge parseExcel.run()"""
        try:
            if not payload.get('fileContent'):
                raise ValueError('No file content provided')
            
            if not payload.get('fileName'):
                raise ValueError('No file name provided')
            
            # Convert base64 to bytes
            file_content = base64.b64decode(payload['fileContent'])
            
            # Parse the file
            raw_records = self.read_any_table(file_content, payload['fileName'])
            
            # Normalize records
            columns_cfg = payload.get('columnsCfg', self.DEFAULT_COLUMNS_CFG)
            records = self.normalize_records(raw_records, columns_cfg)
            
            # Group by epic
            epics = self.group_by_epic(records)
            
            return {
                'records': records,
                'epics': epics
            }
            
        except Exception as e:
            raise ValueError(f'Failed to parse file: {str(e)}')


class ForgeLLMValidator:
    """Python implementation of the original Forge callLLM function"""
    
    def validate_requirement(self, requirement: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a single requirement"""
        issues = []
        
        # Check required fields
        if not requirement.get('requirement_id') or not str(requirement['requirement_id']).strip():
            issues.append('Missing requirement_id')
        
        if not requirement.get('requirement') or not str(requirement['requirement']).strip():
            issues.append(f"Missing requirement (Epic name) for {requirement.get('requirement_id', 'unknown')}")
        
        if not requirement.get('description') or not str(requirement['description']).strip():
            issues.append(f"Missing description for {requirement.get('requirement_id', 'unknown')}")
        
        # Check priority format
        priority = str(requirement.get('priority', '')).upper()
        if priority and priority not in ['P0', 'P1', 'P2', 'P3', 'P4']:
            issues.append(f"Invalid priority '{priority}' for {requirement.get('requirement_id', 'unknown')}. Expected P0-P4")
        
        # Check description length
        description = str(requirement.get('description', ''))
        if description and len(description.split()) < 3:
            issues.append(f"Description too short for {requirement.get('requirement_id', 'unknown')}. Consider adding more details.")
        
        return len(issues) == 0, issues
    
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Main validation function - replicates Forge callLLM.run()"""
        try:
            requirements = payload.get('requirements', [])
            if not isinstance(requirements, list):
                raise ValueError('No requirements array provided')
            
            warnings = []
            errors = []
            validated_requirements = []
            
            for requirement in requirements:
                is_valid, issues = self.validate_requirement(requirement)
                
                if not is_valid:
                    errors.extend(issues)
                elif issues:
                    warnings.extend(issues)
                
                validated_requirements.append(requirement)
            
            return {
                'isValid': len(errors) == 0,
                'validatedRequirements': validated_requirements,
                'warnings': warnings,
                'errors': errors
            }
            
        except Exception as e:
            raise ValueError(f'LLM validation failed: {str(e)}')


class ForgeJiraCreator:
    """Python implementation of the original Forge createJira function"""
    
    DEFAULT_PRIORITY_MAPPING = {
        'P0': 'Highest',
        'P1': 'High',
        'P2': 'Medium',
        'P3': 'Low',
        'P4': 'Lowest'
    }
    
    def __init__(self, base_url: str, email: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.auth = base64.b64encode(f"{email}:{api_token}".encode()).decode()
    
    def _make_request(self, method: str, url: str, data: Dict = None, max_retries: int = 4) -> requests.Response:
        """Make HTTP request with retry logic"""
        headers = {
            'Authorization': f'Basic {self.auth}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        for attempt in range(max_retries):
            try:
                if method.upper() == 'GET':
                    response = requests.get(url, headers=headers, timeout=30)
                elif method.upper() == 'POST':
                    response = requests.post(url, headers=headers, json=data, timeout=30)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                # Retry on specific status codes
                if response.status_code in [429, 500, 502, 503, 504] and attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)
                    continue
                raise e
        
        raise Exception('Max retries exceeded')
    
    def _jql_escape_literal(self, text: str) -> str:
        """Escape text for JQL queries"""
        if not text:
            return ''
        return str(text).replace('\\', '\\\\').replace('"', '\\"')
    
    def _search_issue_by_requirement_id(self, project_key: str, requirement_id: str, issue_type: str = None) -> Optional[Dict]:
        """Search for existing issue by requirement ID"""
        if not requirement_id:
            return None
        
        escaped_id = self._jql_escape_literal(requirement_id)
        jql = f'project = "{project_key}" AND summary ~ "{escaped_id}"'
        if issue_type:
            jql += f' AND issuetype = "{issue_type}"'
        
        url = f"{self.base_url}/rest/api/3/search/jql?jql={requests.utils.quote(jql)}&maxResults=1"
        response = self._make_request('GET', url)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('issues', [{}])[0] if data.get('issues') else None
        return None
    
    def _get_epic_by_name(self, project_key: str, epic_name: str) -> Optional[Dict]:
        """Get existing epic by name"""
        escaped_name = self._jql_escape_literal(epic_name)
        jql = f'project = "{project_key}" AND issuetype = "Epic" AND summary ~ "{escaped_name}"'
        
        url = f"{self.base_url}/rest/api/3/search/jql?jql={requests.utils.quote(jql)}&maxResults=1"
        response = self._make_request('GET', url)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('issues', [{}])[0] if data.get('issues') else None
        return None
    
    def _create_epic(self, project_key: str, epic_name: str, epic_description: str) -> Dict:
        """Create new epic"""
        body = {
            'fields': {
                'project': {'key': project_key},
                'summary': epic_name,
                'issuetype': {'name': 'Epic'},
                'description': {
                    'type': 'doc',
                    'version': 1,
                    'content': [{
                        'type': 'paragraph',
                        'content': [{'type': 'text', 'text': epic_description}]
                    }]
                }
            }
        }
        
        url = f"{self.base_url}/rest/api/3/issue"
        response = self._make_request('POST', url, body)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create epic: {response.status_code} - {response.text}")
    
    def _create_story(self, project_key: str, requirement: Dict, epic_id: str) -> Dict:
        """Create new story"""
        priority_mapping = self.DEFAULT_PRIORITY_MAPPING
        priority = str(requirement.get('priority', '')).upper()
        priority_name = priority_mapping.get(priority, 'Medium')
        
        # Build labels
        labels = []
        if requirement.get('domain'):
            labels.append(str(requirement['domain']).replace(' ', '-').lower())
        if requirement.get('subdomain'):
            labels.append(str(requirement['subdomain']).replace(' ', '-').lower())
        if requirement.get('requirement_type'):
            labels.append(str(requirement['requirement_type']).lower())
        
        # Build components
        components = []
        if requirement.get('domain'):
            components.append({'name': str(requirement['domain']).strip()})
        
        fields = {
            'project': {'key': project_key},
            'summary': requirement.get('story_summary', 'Untitled Story'),
            'issuetype': {'name': 'Story'},
            'description': {
                'type': 'doc',
                'version': 1,
                'content': [{
                    'type': 'paragraph',
                    'content': [{'type': 'text', 'text': requirement.get('enriched_description', requirement.get('description', ''))}]
                }]
            },
            'priority': {'name': priority_name},
            'labels': labels,
            'parent': {'id': epic_id}
        }
        
        if components:
            fields['components'] = components
        
        body = {'fields': fields}
        url = f"{self.base_url}/rest/api/3/issue"
        response = self._make_request('POST', url, body)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create story: {response.status_code} - {response.text}")
    
    def _make_story_summary(self, requirement_id: str, description: str, max_words: int = 10) -> str:
        """Create story summary from requirement ID and description"""
        if not description or not description.strip():
            return f"[{requirement_id}]" if requirement_id else 'Untitled Story'
        
        words = description.strip().split()[:max_words]
        summary = ' '.join(words)
        
        bracket = f"[{requirement_id}]" if requirement_id and requirement_id.strip() else ''
        space = ' ' if bracket and summary else ''
        
        return bracket + space + summary or 'Untitled Story'
    
    def _aggregate_epic_description(self, requirements: List[Dict]) -> str:
        """Aggregate descriptions for epic"""
        descriptions = [req.get('description', '') for req in requirements if req.get('description')]
        return '\n\n'.join(descriptions)
    
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Main Jira creation function - replicates Forge createJira.run()"""
        try:
            epics = payload.get('epics', {})
            if not isinstance(epics, dict):
                raise ValueError('No epics data provided')
            
            jira_config = payload.get('jiraConfig', {})
            project_key = jira_config.get('projectKey', '')
            
            if not project_key:
                raise ValueError('Missing project key in Jira configuration')
            
            results = {
                'epicsCreated': 0,
                'storiesCreated': 0,
                'errors': []
            }
            
            # Process each epic group
            for epic_name, requirements in epics.items():
                if not epic_name or epic_name == 'Unnamed Epic':
                    continue
                
                try:
                    # Check if epic exists
                    epic_issue = self._get_epic_by_name(project_key, epic_name)
                    
                    if not epic_issue:
                        epic_description = self._aggregate_epic_description(requirements)
                        epic_issue = self._create_epic(project_key, epic_name, epic_description)
                        results['epicsCreated'] += 1
                    
                    epic_id = epic_issue['id']
                    
                    # Create stories
                    for requirement in requirements:
                        try:
                            story_summary = self._make_story_summary(
                                requirement.get('requirement_id', ''),
                                requirement.get('description', ''),
                                10
                            )
                            
                            # Check if story exists
                            existing_story = self._search_issue_by_requirement_id(
                                project_key,
                                requirement.get('requirement_id', ''),
                                'Story'
                            )
                            
                            if not existing_story:
                                requirement['story_summary'] = story_summary
                                requirement['enriched_description'] = requirement.get('description', '')
                                
                                self._create_story(project_key, requirement, epic_id)
                                results['storiesCreated'] += 1
                        
                        except Exception as story_error:
                            error_msg = f"Failed to create story for {requirement.get('requirement_id', 'unknown')}: {str(story_error)}"
                            results['errors'].append(error_msg)
                
                except Exception as epic_error:
                    error_msg = f"Failed to process epic {epic_name}: {str(epic_error)}"
                    results['errors'].append(error_msg)
            
            return {
                'success': len(results['errors']) == 0,
                'message': f"Successfully created {results['epicsCreated']} epics and {results['storiesCreated']} stories",
                'results': results
            }
            
        except Exception as e:
            raise ValueError(f'Jira ticket creation failed: {str(e)}')


class ForgeWorkflowProcessor:
    """Main workflow processor that replicates the original Forge resolver logic"""
    
    def __init__(self):
        self.excel_parser = ForgeExcelParser()
        self.llm_validator = ForgeLLMValidator()
    
    def process_workflow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Main workflow processing function - replicates Forge resolver.processWorkflow()"""
        try:
            file_name = payload.get('fileName', 'Unknown File')
            project_key = payload.get('jiraConfig', {}).get('projectKey', 'N/A')
            
            # Step 1: Parse Excel
            parse_result = self.excel_parser.run(payload)
            
            # Step 2: Validate with LLM
            validation_result = self.llm_validator.run({
                'requirements': parse_result['records']
            })
            
            if not validation_result['isValid']:
                return {
                    'success': False,
                    'error': 'Data validation failed',
                    'validationErrors': validation_result['errors'],
                    'validationWarnings': validation_result['warnings']
                }
            
            # Step 3: Create Jira tickets
            jira_creator = ForgeJiraCreator(
                payload['jiraConfig']['baseUrl'],
                payload['jiraConfig']['email'],
                payload['jiraConfig']['apiToken']
            )
            
            jira_result = jira_creator.run({
                'epics': parse_result['epics'],
                'jiraConfig': payload['jiraConfig']
            })
            
            return {
                'success': True,
                'parsed': {
                    'recordCount': len(parse_result['records']),
                    'epicCount': len(parse_result['epics'])
                },
                'validation': {
                    'warnings': validation_result['warnings'],
                    'errorsCount': len(validation_result['errors'])
                },
                'jira': jira_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
