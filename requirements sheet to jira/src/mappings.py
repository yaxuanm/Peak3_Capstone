from typing import Any, Dict, List, Optional, Tuple

from utils import coalesce_str, ensure_list, take_first_words


def map_priority(priority_text: str, priority_map: Dict[str, str]) -> Optional[str]:
    key = coalesce_str(priority_text).upper()
    return priority_map.get(key)


def build_labels(record: Dict[str, Any], label_fields: List[str]) -> List[str]:
    labels: List[str] = []
    for field in label_fields:
        value = coalesce_str(record.get(field))
        if value:
            labels.append(value.replace(" ", "-").lower())
    # de-duplicate preserving order
    seen = set()
    unique = []
    for l in labels:
        if l not in seen:
            seen.add(l)
            unique.append(l)
    return unique


def build_components(record: Dict[str, Any], component_from: Optional[str]) -> List[Dict[str, str]]:
    if not component_from:
        return []
    value = coalesce_str(record.get(component_from))
    return [{"name": value}] if value else []


def make_story_summary(requirement_id: str, description: str, max_words: int) -> str:
    short = take_first_words(description, max_words)
    bracket = f"[{requirement_id}]" if requirement_id else ""
    space = " " if bracket and short else ""
    return f"{bracket}{space}{short}" if (bracket or short) else "Untitled Story"
