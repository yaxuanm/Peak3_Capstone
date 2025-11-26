from typing import Any, Dict, List, Optional

import time
import requests

from utils import jql_escape_literal


class JiraClient:
    def __init__(
        self,
        base_url: str,
        email: str,
        api_token: str,
        project_key: str,
        epic_link_field_key: Optional[str] = None,
        dry_run: bool = False,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.auth = (email, api_token)
        self.project_key = project_key
        self.epic_link_field_key = epic_link_field_key
        self.dry_run = dry_run
        self._session = requests.Session()
        self._session.auth = self.auth
        self._session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

    def _request_with_retry(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        if self.dry_run:
            return {"dryRun": True, "method": method, "path": path, **({k: v for k, v in kwargs.items() if v is not None})}
        url = f"{self.base_url}{path}"
        backoff = 1.0
        for attempt in range(4):
            resp = self._session.request(method, url, timeout=60, **kwargs)
            if resp.status_code in (429, 500, 502, 503, 504):
                if attempt < 3:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
            # Better error logging
            if resp.status_code >= 400:
                error_msg = f"Jira API Error {resp.status_code}:"
                print(error_msg)
                print(f"URL: {url}")
                print(f"Method: {method}")
                print(f"Auth Email: {self.auth[0]}")
                print(f"Auth Token: {self.auth[1][:20]}..." if len(self.auth[1]) > 20 else f"Auth Token: {self.auth[1]}")
                if kwargs.get('json'):
                    # Don't print full request body if it's too large
                    req_body = kwargs.get('json')
                    if isinstance(req_body, dict) and 'fields' in req_body:
                        print(f"Request fields: {list(req_body.get('fields', {}).keys())}")
                    else:
                        print(f"Request body: {req_body}")
                print(f"Response: {resp.text}")
                print("="*50)
                
                # Provide helpful error messages for common issues
                if resp.status_code == 401:
                    print("\n[认证错误] 可能的原因:")
                    print("1. API Token 已过期或无效")
                    print("2. Email 地址不正确")
                    print("3. API Token 格式错误（应使用完整的API Token，不是密码）")
                    print("4. 账户可能被禁用或没有API访问权限")
                    print("\n解决方案:")
                    print("1. 访问 https://id.atlassian.com/manage-profile/security/api-tokens")
                    print("2. 创建新的API Token")
                    print("3. 确保使用正确的Email地址（与Jira账户关联的邮箱）")
                    print("4. 确保API Token完整复制，没有多余的空格或换行")
                    print("="*50)
            resp.raise_for_status()
            if resp.content:
                return resp.json()
            return {}
        # Fallback (should not reach)
        resp.raise_for_status()
        return {}

    def _post(self, path: str, json_body: Dict[str, Any]) -> Dict[str, Any]:
        return self._request_with_retry("POST", path, json=json_body)

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request_with_retry("GET", path, params=params)

    def search_issue_by_requirement_id(self, requirement_id: str, issue_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search for existing issue by Requirement ID in summary field
        
        Uses JQL fuzzy search (~) then verifies exact match in code,
        since JQL doesn't support exact string matching on summary field.
        """
        esc = jql_escape_literal(requirement_id)
        jql = f'project = "{self.project_key}" AND summary ~ "{esc}"'
        if issue_type:
            jql += f' AND issuetype = "{jql_escape_literal(issue_type)}"'
        try:
            # Use the standard search endpoint, get more results to find exact match
            data = self._get("/rest/api/3/search", params={"jql": jql, "maxResults": 10})
        except Exception:
            # Fallback: treat JQL 400 as not found, proceed with creation
            return None
        if data.get("dryRun"):
            return None
        issues = data.get("issues", [])
        
        # Verify exact match - requirement_id should be at the start of summary
        # Format is typically: "REQ-ID: Description" or "REQ-ID - Description"
        for issue in issues:
            summary = issue.get('fields', {}).get('summary', '')
            # Check if requirement_id is at the beginning of summary
            if summary.startswith(requirement_id) or f"[{requirement_id}]" in summary:
                return issue
        
        return None

    def get_epic_by_name(self, epic_name: str) -> Optional[Dict[str, Any]]:
        esc = jql_escape_literal(epic_name)
        # Use ~ operator for summary field (fuzzy match) since = is not supported
        jql = f'project = "{self.project_key}" AND issuetype = "Epic" AND summary ~ "{esc}"'
        try:
            data = self._get("/rest/api/3/search/jql", params={"jql": jql, "maxResults": 1})
        except Exception:
            return None
        if data.get("dryRun"):
            return None
        issues = data.get("issues", [])
        return issues[0] if issues else None

    def create_epic(self, epic_name: str, epic_description: str) -> Dict[str, Any]:
        # Jira Cloud 要求 description 使用 Atlassian Document Format (ADF)
        adf_desc = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": epic_description or ""}]
                }
            ]
        } if epic_description else None

        body = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": epic_name,
                "issuetype": {"name": "Epic"},
            }
        }
        if adf_desc:
            body["fields"]["description"] = adf_desc
        return self._post("/rest/api/3/issue", body)

    def create_story(
        self,
        summary: str,
        description: str,
        priority_name: Optional[str],
        epic_issue_id: Optional[str],
        epic_link_field_key: Optional[str],
        labels: List[str],
        components: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        # Jira Cloud 要求 description 使用 Atlassian Document Format (ADF)
        adf_desc = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": description or ""}]
                }
            ]
        } if description else None

        fields: Dict[str, Any] = {
            "project": {"key": self.project_key},
            "summary": summary,
            "issuetype": {"name": "Story"},
        }
        if adf_desc:
            fields["description"] = adf_desc
        if priority_name:
            fields["priority"] = {"name": priority_name}
        # Team-managed projects use parent field instead of Epic Link
        if epic_issue_id:
            fields["parent"] = {"id": epic_issue_id}
        if labels:
            fields["labels"] = labels
        # Temporarily comment out component since it's not specified
        # if components:
        #     fields["components"] = components

        return self._post("/rest/api/3/issue", {"fields": fields})
