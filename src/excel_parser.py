from typing import Any, Dict, List

import os
import pandas as pd


def _read_any_table(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext in [".xlsx", ".xlsm", ".xls"]:
        return pd.read_excel(path, engine="openpyxl")
    if ext in [".csv", ".txt"]:
        return pd.read_csv(path, dtype=str)
    # fallback try excel
    return pd.read_excel(path, engine="openpyxl")


def read_excel_records(excel_path: str) -> List[Dict[str, Any]]:
    df = _read_any_table(excel_path)
    df = df.fillna("")
    records: List[Dict[str, Any]] = df.to_dict(orient="records")
    return records


def normalize_records(records: List[Dict[str, Any]], columns_cfg: Dict[str, str]) -> List[Dict[str, Any]]:
    """Rename and project columns using config mapping to normalized keys.

    columns_cfg expects keys: requirement_id, requirement, description, priority, domain, subdomain, requirement_type
    """
    result: List[Dict[str, Any]] = []
    for raw in records:
        item: Dict[str, Any] = {
            "requirement_id": raw.get(columns_cfg.get("requirement_id", "Requirement ID"), ""),
            "requirement": raw.get(columns_cfg.get("requirement", "Requirement"), ""),
            "description": raw.get(columns_cfg.get("description", "Description"), ""),
            "priority": raw.get(columns_cfg.get("priority", "Priority"), ""),
            "domain": raw.get(columns_cfg.get("domain", "Domain"), ""),
            "subdomain": raw.get(columns_cfg.get("subdomain", "Sub-domain"), ""),
            "requirement_type": raw.get(columns_cfg.get("requirement_type", "Requirement type"), ""),
        }
        result.append(item)
    return result
