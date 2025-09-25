import os
import argparse
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from .excel_parser import normalize_records, read_excel_records
from .jira_client import JiraClient
from .mappings import build_components, build_labels, make_story_summary, map_priority
from .utils import coalesce_str, load_env, load_yaml_config


def group_by_epic(records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in records:
        epic_name = coalesce_str(r.get("requirement"))
        groups[epic_name].append(r)
    return groups


def aggregate_epic_description(items: List[Dict[str, Any]]) -> str:
    # 简单聚合：按描述拼接；后续可接LLM摘要
    descriptions = [coalesce_str(i.get("description")) for i in items if coalesce_str(i.get("description"))]
    return "\n\n".join(descriptions)


def run(excel_path: str, config_path: str, dry_run: bool) -> None:
    load_env()
    cfg = load_yaml_config(config_path)

    # 读取我们当前 config.yml 的结构
    excel_cfg: Dict[str, Any] = cfg.get("excel", {})
    columns_cfg: Dict[str, str] = excel_cfg.get("columns", {})
    jira_cfg: Dict[str, Any] = cfg.get("jira", {})
    priority_map: Dict[str, str] = jira_cfg.get("priority_mapping", {})
    story_title_words: int = int(cfg.get("texting", {}).get("story_title_words", 10))

    base_url = jira_cfg.get("base_url") or coalesce_str(jira_cfg.get("baseUrl")) or coalesce_str(jira_cfg.get("url"))
    if not base_url:
        base_url = coalesce_str(os.getenv("JIRA_BASE_URL"))
    email = coalesce_str(os.getenv("JIRA_EMAIL"))
    token = coalesce_str(os.getenv("JIRA_API_TOKEN"))
    project_key = coalesce_str(jira_cfg.get("project_key")) or coalesce_str(os.getenv("JIRA_PROJECT_KEY"))
    epic_link_field_key = coalesce_str(jira_cfg.get("epic_link_field_key")) or None

    # DryRun 模式下跳过凭证校验
    if not (base_url and email and token and project_key):
        if not dry_run:
            raise RuntimeError("Missing Jira credentials or project key. Please set env and config correctly.")

    component_from = jira_cfg.get("component_from")
    labels_from = cfg.get("jira", {}).get("labels_from", [])

    records_raw = read_excel_records(excel_path)
    records = normalize_records(records_raw, columns_cfg)

    groups = group_by_epic(records)

    # DryRun: 仅打印将要创建的 Epic 与 Story，不做任何 API 调用
    if dry_run:
        for epic_name, items in groups.items():
            if not epic_name:
                continue
            epic_desc = aggregate_epic_description(items)
            print(f"[DRY RUN] Would create Epic: {epic_name}")
            print(f"[DRY RUN]   Epic Description Preview: {epic_desc[:120]}...")
            for row in items:
                req_id = coalesce_str(row.get("requirement_id"))
                description = coalesce_str(row.get("description"))
                summary = make_story_summary(req_id, description, story_title_words)
                priority_name = map_priority(coalesce_str(row.get("priority")), priority_map)
                labels = build_labels(row, labels_from)
                components = build_components(row, component_from)
                print(f"[DRY RUN]   Would create Story: {summary}")
                print(f"[DRY RUN]     Priority: {priority_name}, Labels: {labels}, Components: {components}")
        return

    # 非 DryRun，执行真实调用
    client = JiraClient(
        base_url=base_url,
        email=email,
        api_token=token,
        project_key=project_key,
        epic_link_field_key=epic_link_field_key,
        dry_run=dry_run,
    )

    for epic_name, items in groups.items():
        if not epic_name:
            continue
        # Idempotent epic create or fetch
        epic_issue = client.get_epic_by_name(epic_name)
        if not epic_issue:
            epic_desc = aggregate_epic_description(items)
            epic_issue = client.create_epic(epic_name=epic_name, epic_description=epic_desc)
        epic_id: Optional[str] = None
        if epic_issue and not epic_issue.get("dryRun"):
            epic_id = epic_issue.get("id")

        # Create stories
        for row in items:
            req_id = coalesce_str(row.get("requirement_id"))
            description = coalesce_str(row.get("description"))
            summary = make_story_summary(req_id, description, story_title_words)

            # Idempotent story by summary
            existing = client.search_issue_by_summary(summary, issue_type="Story")
            if existing:
                continue

            priority_name = map_priority(coalesce_str(row.get("priority")), priority_map)
            labels = build_labels(row, labels_from)
            components = build_components(row, component_from)

            client.create_story(
                summary=summary,
                description=description,
                priority_name=priority_name,
                epic_issue_id=epic_id,
                epic_link_field_key=epic_link_field_key,
                labels=labels,
                components=components,
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Excel Requirements → Jira Tickets")
    parser.add_argument("-ExcelPath", required=True, help="Path to Excel file")
    parser.add_argument("-ConfigPath", required=True, help="Path to YAML config")
    parser.add_argument("-DryRun", action="store_true", help="Dry run (no API calls)")
    args = parser.parse_args()

    run(excel_path=args.ExcelPath, config_path=args.ConfigPath, dry_run=args.DryRun)


if __name__ == "__main__":
    main()
