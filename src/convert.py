import os
import argparse
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from excel_parser import normalize_records, read_excel_records
from jira_client import JiraClient
from mappings import build_components, build_labels, make_story_summary, map_priority
from utils import coalesce_str, load_env, load_yaml_config
from data_quality_checker import DataQualityChecker


def group_by_epic(records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in records:
        epic_name = coalesce_str(r.get("requirement"))
        groups[epic_name].append(r)
    return groups


def aggregate_epic_description(items: List[Dict[str, Any]]) -> str:
    # Simple aggregation: concatenate descriptions; can be enhanced with LLM summarization later
    descriptions = [coalesce_str(i.get("description")) for i in items if coalesce_str(i.get("description"))]
    return "\n\n".join(descriptions)


def perform_data_quality_check(excel_path: str, enable_quality_check: bool = True, sheet_name: str = "1. Requirements - Internal") -> Optional[List[str]]:
    """
    Perform data quality check on the Excel file before processing.
    
    Args:
        excel_path (str): Path to the Excel file
        enable_quality_check (bool): Whether to enable data quality checking
        sheet_name (str): Name of the Excel sheet to check
        
    Returns:
        Optional[List[str]]: List of quality check results, or None if disabled
    """
    if not enable_quality_check:
        return None
        
    try:
        # Initialize data quality checker
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  Warning: OPENAI_API_KEY not found. Skipping data quality check.")
            return None
            
        quality_checker = DataQualityChecker(api_key)
        
        # Load the Excel file for quality checking
        if excel_path.endswith(".csv"):
            import pandas as pd
            df = pd.read_csv(excel_path)
        else:
            df = quality_checker.load_excel_sheet(excel_path, sheet_name)
        
        print(f"🔍 Performing data quality check on {len(df)} records...")
        
        # Perform quality check
        quality_results = quality_checker.data_quality_check(df)
        
        print("✅ Data quality check completed!")
        return quality_results
        
    except Exception as e:
        print(f"⚠️  Warning: Data quality check failed: {str(e)}")
        print("   Continuing with workflow...")
        return None


def run(excel_path: str, config_path: str, dry_run: bool, enable_quality_check: bool = True) -> None:
    load_env()
    cfg = load_yaml_config(config_path)

    # Read current config.yml structure
    excel_cfg: Dict[str, Any] = cfg.get("excel", {})
    columns_cfg: Dict[str, str] = excel_cfg.get("columns", {})
    sheet_name: str = excel_cfg.get("sheet_name", "1. Requirements - Internal")
    jira_cfg: Dict[str, Any] = cfg.get("jira", {})
    priority_map: Dict[str, str] = jira_cfg.get("priority_mapping", {})
    story_title_words: int = int(cfg.get("texting", {}).get("story_title_words", 10))
    
    # Check if data quality checking is enabled in config
    quality_check_enabled = cfg.get("data_quality", {}).get("enabled", enable_quality_check)

    base_url = jira_cfg.get("base_url") or coalesce_str(jira_cfg.get("baseUrl")) or coalesce_str(jira_cfg.get("url"))
    if not base_url:
        base_url = coalesce_str(os.getenv("JIRA_BASE_URL"))
    email = coalesce_str(os.getenv("JIRA_EMAIL"))
    token = coalesce_str(os.getenv("JIRA_API_TOKEN"))
    project_key = coalesce_str(jira_cfg.get("project_key")) or coalesce_str(os.getenv("JIRA_PROJECT_KEY"))
    epic_link_field_key = coalesce_str(jira_cfg.get("epic_link_field_key")) or None

    # Skip credential validation in DryRun mode
    if not (base_url and email and token and project_key):
        if not dry_run:
            raise RuntimeError("Missing Jira credentials or project key. Please set env and config correctly.")

    component_from = jira_cfg.get("component_from")
    labels_from = cfg.get("jira", {}).get("labels_from", [])

    records_raw = read_excel_records(excel_path, sheet_name)
    records = normalize_records(records_raw, columns_cfg)
    # Guard: filter out empty rows to avoid creating blank tickets
    records = [
        r for r in records
        if coalesce_str(r.get("requirement_id")) and coalesce_str(r.get("requirement"))
    ]

    # Perform data quality check before processing
    quality_results = perform_data_quality_check(excel_path, quality_check_enabled, sheet_name)
    if quality_results:
        print("\n" + "="*80)
        print("DATA QUALITY ANALYSIS RESULTS")
        print("="*80)
        for i, result in enumerate(quality_results, 1):
            print(f"\n--- Requirement {i} Analysis ---")
            print(result)
        print("="*80 + "\n")

    groups = group_by_epic(records)

    # DryRun: Only print Epics and Stories to be created, no API calls
    if dry_run:
        for epic_name, items in groups.items():
            if not epic_name:
                continue
            epic_desc = aggregate_epic_description(items)
            print(f"[DRY RUN] Would create Epic: {epic_name}")
            print(f"[DRY RUN]   Epic Description Preview: {epic_desc[:120]}...")
            for row in items:
                req_id = coalesce_str(row.get("requirement_id"))
                if not req_id:
                    continue
                description = coalesce_str(row.get("description"))
                summary = make_story_summary(req_id, description, story_title_words)
                if summary == "Untitled Story":
                    continue
                priority_name = map_priority(coalesce_str(row.get("priority")), priority_map)
                labels = build_labels(row, labels_from)
                components = build_components(row, component_from)
                print(f"[DRY RUN]   Would create Story: {summary}")
                print(f"[DRY RUN]     Priority: {priority_name}, Labels: {labels}, Components: {components}")
        return

    # Non-DryRun, execute real API calls
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
            if not req_id:
                continue
            description = coalesce_str(row.get("description"))
            summary = make_story_summary(req_id, description, story_title_words)
            if summary == "Untitled Story":
                continue

            # Idempotent story by requirement ID
            existing = client.search_issue_by_requirement_id(req_id, issue_type="Story")
            if existing:
                print(f"[SKIP] Story already exists for Requirement ID: {req_id}")
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
    parser.add_argument("-SkipQualityCheck", action="store_true", help="Skip data quality check")
    args = parser.parse_args()

    run(excel_path=args.ExcelPath, config_path=args.ConfigPath, dry_run=args.DryRun, enable_quality_check=not args.SkipQualityCheck)


if __name__ == "__main__":
    main()
