from typing import Any, Dict, List, Optional

import time
import requests

from .utils import jql_escape_literal


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
        """Search for existing issue by Requirement ID in summary field"""
        esc = jql_escape_literal(requirement_id)
        jql = f'project = "{self.project_key}" AND summary ~ "{esc}"'
        if issue_type:
            jql += f' AND issuetype = "{jql_escape_literal(issue_type)}"'
        try:
            data = self._get("/rest/api/3/search", params={"jql": jql, "maxResults": 1})
        except Exception:
            # Fallback: treat JQL 400 as not found, proceed with creation
            return None
        if data.get("dryRun"):
            return None
        issues = data.get("issues", [])
        return issues[0] if issues else None

    def get_epic_by_name(self, epic_name: str) -> Optional[Dict[str, Any]]:
        esc = jql_escape_literal(epic_name)
        # 先尝试用 Epic Name（公司管理项目常用）；失败再退回 summary
        candidates = [
            f'project = "{self.project_key}" AND issuetype = "Epic" AND "Epic Name" = "{esc}"',
            f'project = "{self.project_key}" AND issuetype = "Epic" AND summary = "{esc}"',
        ]
        for jql in candidates:
            try:
                data = self._get("/rest/api/3/search", params={"jql": jql, "maxResults": 1})
            except Exception:
                continue
            if data.get("dryRun"):
                return None
            issues = data.get("issues", [])
            if issues:
                return issues[0]
        return None

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
        if components:
            fields["components"] = components

        return self._post("/rest/api/3/issue", {"fields": fields})
