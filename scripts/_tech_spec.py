from __future__ import annotations

import re
from pathlib import Path


def _section_text(markdown: str, title: str) -> str:
    lines = markdown.splitlines()
    start = -1
    level = 0
    for i, line in enumerate(lines):
        match = re.match(r"^(#+)\s+(.*)$", line.strip())
        if not match:
            continue
        if match.group(2).strip().lower() == title.lower():
            start = i + 1
            level = len(match.group(1))
            break
    if start < 0:
        return ""

    end = len(lines)
    for j in range(start, len(lines)):
        match = re.match(r"^(#+)\s+", lines[j].strip())
        if match and len(match.group(1)) <= level:
            end = j
            break
    return "\n".join(lines[start:end]).strip()


def _extract_kv_bullets(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^\s*-\s*([^:]+):\s*(.*)$", line.strip())
        if not match:
            continue
        key = match.group(1).strip().lower()
        value = match.group(2).strip().strip("`").strip()
        result[key] = value
    return result


def _contains_placeholder(value: str) -> bool:
    return "{{" in value or "}}" in value


def _has_meaningful_table_rows(text: str) -> bool:
    for line in text.splitlines():
        striped = line.strip()
        if not striped.startswith("|"):
            continue
        if re.match(r"^\|\s*[-: ]+\|\s*[-: |]+\|?$", striped):
            continue
        if "Repository Path" in striped or "ID" in striped:
            continue
        if _contains_placeholder(striped):
            continue
        # Any non-header row is sufficient for now.
        return True
    return False


def _extract_acceptance_criteria(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if match:
            item = match.group(1).strip()
            if item and not _contains_placeholder(item):
                items.append(item)
    return items


def parse_and_validate_refined_tech_spec(path: str) -> dict[str, object]:
    markdown = Path(path).read_text(encoding="utf-8")
    errors: list[str] = []

    doc_control = _extract_kv_bullets(_section_text(markdown, "1. Document Control"))
    story_draft = _extract_kv_bullets(_section_text(markdown, "11.1 Story Draft"))
    impacted = _section_text(markdown, "6.2 Impacted Components, Classes, and Methods")
    qa_scenarios = _section_text(markdown, "9.2 Test Scenarios")
    ac_section = _section_text(markdown, "11.2 Acceptance Criteria (AC)")
    ac_items = _extract_acceptance_criteria(ac_section)

    jira_project_key = doc_control.get("jira project key", "").strip("`").strip()
    story_type = story_draft.get("story type", "").strip("`").strip()
    story_summary = story_draft.get("summary", "").strip("`").strip()
    story_problem = story_draft.get("problem", "").strip("`").strip()
    story_solution = story_draft.get("proposed solution", "").strip("`").strip()
    story_scope = story_draft.get("scope", "").strip("`").strip()
    story_dependencies = story_draft.get("dependencies", "").strip("`").strip()

    if not jira_project_key or _contains_placeholder(jira_project_key):
        errors.append("Section 1 must include a concrete `Jira Project Key`.")
    if not story_type or _contains_placeholder(story_type):
        errors.append("Section 11.1 must include concrete `Story Type` (e.g., Story/Bug).")
    if not story_summary or _contains_placeholder(story_summary):
        errors.append("Section 11.1 must include concrete `Summary`.")
    if not _has_meaningful_table_rows(impacted):
        errors.append("Section 6.2 must include at least one impacted class/method row.")
    if not _has_meaningful_table_rows(qa_scenarios):
        errors.append("Section 9.2 must include at least one QA test scenario row.")
    if not ac_items:
        errors.append("Section 11.2 must include at least one non-placeholder acceptance criterion.")

    description_lines = [
        "Problem:",
        story_problem or "Not provided.",
        "",
        "Proposed Solution:",
        story_solution or "Not provided.",
        "",
        "Scope:",
        story_scope or "Not provided.",
        "",
        "Dependencies:",
        story_dependencies or "Not provided.",
        "",
        "Acceptance Criteria:",
    ]
    for idx, item in enumerate(ac_items, start=1):
        description_lines.append(f"{idx}. {item}")

    return {
        "errors": errors,
        "jira_project_key": jira_project_key,
        "story_type": story_type,
        "story_summary": story_summary,
        "story_description": "\n".join(description_lines).strip(),
        "acceptance_criteria": ac_items,
    }
