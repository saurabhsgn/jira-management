"""Create a technical specification draft from FDR input.

Interactive, no-assumption workflow:
1) Ask project name first.
2) Accept FDR from text, Confluence URL, PDF, or file.
3) Discover existing functionality from local code.
4) Produce spec draft and Jira story plan for approval.

Usage:
  python scripts/create_tech_spec_from_fdr.py --help
"""

from __future__ import annotations

import argparse
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from _config import ConfigError, load_config
from _confluence import ConfluenceClient
from _jira import JiraClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a tech spec draft from FDR.")
    parser.add_argument("--project-name", required=False)
    parser.add_argument("--jira-project-key", required=False)
    parser.add_argument("--fdr-text", required=False, help="Direct requirement text.")
    parser.add_argument("--fdr-file", required=False, help="Path to text/markdown file.")
    parser.add_argument("--fdr-pdf", required=False, help="Path to PDF file.")
    parser.add_argument("--confluence-url", required=False, help="Confluence page URL.")
    parser.add_argument("--output", default="outputs/tech_spec_draft.md")
    parser.add_argument("--jira-plan-output", default="outputs/jira_plan_draft.json")
    parser.add_argument("--interactive", action="store_true", default=True)
    parser.add_argument("--no-interactive", action="store_false", dest="interactive")
    return parser


def _input_value(label: str, current: str | None = None, required: bool = False) -> str | None:
    if current:
        return current
    value = input(f"{label}: ").strip()
    if not value and required:
        print(f"{label} is required.")
        return _input_value(label, None, required=True)
    return value or None


def _extract_page_id_from_url(url: str) -> str | None:
    match = re.search(r"/pages/(\d+)", url)
    if match:
        return match.group(1)

    parsed = urlparse(url)
    query = parsed.query or ""
    for piece in query.split("&"):
        if piece.startswith("pageId="):
            return piece.split("=", 1)[1]
    return None


def _adf_to_text(node: Any) -> str:
    if isinstance(node, dict):
        if node.get("type") == "text":
            return node.get("text", "")
        return "".join(_adf_to_text(item) for item in node.get("content", []))
    if isinstance(node, list):
        return "".join(_adf_to_text(item) for item in node)
    return ""


def _load_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:
        raise RuntimeError("PDF input requires 'pypdf'. Install with: pip install pypdf") from exc

    reader = PdfReader(str(path))
    text_parts: list[str] = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts).strip()


def _load_fdr_text(args: argparse.Namespace, confluence_client: ConfluenceClient | None) -> tuple[str, str]:
    if args.fdr_text:
        return args.fdr_text.strip(), "plain-text"

    if args.fdr_file:
        content = Path(args.fdr_file).read_text(encoding="utf-8")
        return content.strip(), f"file:{args.fdr_file}"

    if args.fdr_pdf:
        content = _load_pdf_text(Path(args.fdr_pdf))
        return content.strip(), f"pdf:{args.fdr_pdf}"

    if args.confluence_url:
        if confluence_client is None:
            raise RuntimeError("Confluence client unavailable. Check config.json.")
        page_id = _extract_page_id_from_url(args.confluence_url)
        if not page_id:
            raise RuntimeError("Unable to parse Confluence page id from URL.")
        response = confluence_client.request(
            "GET",
            f"/content/{page_id}",
            params={"expand": "body.storage,title"},
        ).json()
        title = response.get("title", "")
        storage = response.get("body", {}).get("storage", {}).get("value", "")
        stripped = re.sub(r"<[^>]+>", " ", storage)
        return f"{title}\n\n{stripped}".strip(), f"confluence:{page_id}"

    raise RuntimeError("No FDR source provided.")


def _discover_local_code(root: Path) -> dict[str, Any]:
    from discover_existing_functionality import _scan  # local project import

    return _scan(root, 25)


def _discover_jira_context(jira: JiraClient, project_key: str) -> dict[str, Any]:
    payload = {"jql": f"project = {project_key} ORDER BY updated DESC", "maxResults": 10}
    response = jira.request("POST", "/search/jql", json=payload).json()
    issues = response.get("issues", [])
    result = []
    for issue in issues:
        fields = issue.get("fields", {})
        result.append(
            {
                "key": issue.get("key"),
                "summary": fields.get("summary"),
                "type": (fields.get("issuetype") or {}).get("name"),
                "status": (fields.get("status") or {}).get("name"),
            }
        )
    return {"count": len(result), "issues": result}


def _discover_confluence_context(confluence: ConfluenceClient, url: str | None) -> dict[str, Any]:
    if not url:
        return {"count": 0, "pages": []}
    page_id = _extract_page_id_from_url(url)
    if not page_id:
        return {"count": 0, "pages": []}
    response = confluence.request("GET", f"/content/{page_id}", params={"expand": "title,space"}).json()
    return {
        "count": 1,
        "pages": [
            {
                "id": response.get("id"),
                "title": response.get("title"),
                "space": (response.get("space") or {}).get("key"),
            }
        ],
    }


def _split_requirement_topics(text: str) -> list[str]:
    lines = [line.strip("- *\t ") for line in text.splitlines() if line.strip()]
    candidates = [line for line in lines if len(line.split()) >= 4]
    if not candidates:
        return [text[:120].strip()] if text.strip() else []
    return candidates[:10]


def _build_story_candidates(project_key: str, topics: list[str]) -> list[dict[str, str]]:
    stories: list[dict[str, str]] = []
    for idx, topic in enumerate(topics, start=1):
        summary = topic if len(topic) <= 120 else topic[:117] + "..."
        stories.append(
            {
                "id": f"S{idx:02d}",
                "type": "Story",
                "project_key": project_key,
                "summary": summary,
                "description": f"Derived from FDR topic: {topic}",
                "status": "draft",
            }
        )
    if not stories:
        stories.append(
            {
                "id": "S01",
                "type": "Story",
                "project_key": project_key,
                "summary": "Implement requirement from provided FDR",
                "description": "Draft story generated because no explicit topics were parsed.",
                "status": "draft",
            }
        )
    return stories


def _render_list(items: list[str], empty: str = "- None") -> str:
    if not items:
        return empty
    return "\n".join(f"- {item}" for item in items)


def _render_issues(issues: list[dict[str, Any]]) -> str:
    if not issues:
        return "- No related Jira issues discovered."
    return "\n".join(f"- {i['key']}: {i['type']} | {i['status']} | {i['summary']}" for i in issues)


def _render_stories(stories: list[dict[str, str]]) -> str:
    lines: list[str] = []
    for s in stories:
        lines.append(f"- [{s['type']}] {s['summary']}")
        lines.append(f"  - Draft ID: {s['id']}")
        lines.append(f"  - Description: {s['description']}")
    return "\n".join(lines)


def _write_outputs(
    template_path: Path,
    output_path: Path,
    jira_plan_output: Path,
    replacements: dict[str, str],
    jira_plan: dict[str, Any],
) -> None:
    template = template_path.read_text(encoding="utf-8")
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    jira_plan_output.parent.mkdir(parents=True, exist_ok=True)
    jira_plan_output.write_text(json.dumps(jira_plan, indent=2), encoding="utf-8")


def _prompt_open_questions() -> list[str]:
    questions = []
    print("Enter open questions (blank line to finish):")
    while True:
        item = input("  Question: ").strip()
        if not item:
            break
        questions.append(item)
    return questions


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.interactive:
        args.project_name = _input_value("Project Name (simple word)", args.project_name, required=True)
        args.jira_project_key = _input_value("Jira Project Key", args.jira_project_key, required=True)
        if not any([args.fdr_text, args.fdr_file, args.fdr_pdf, args.confluence_url]):
            source_mode = _input_value(
                "FDR source type (text/file/pdf/confluence-url)",
                required=True,
            )
            if source_mode == "text":
                args.fdr_text = _input_value("Paste FDR text", required=True)
            elif source_mode == "file":
                args.fdr_file = _input_value("FDR file path", required=True)
            elif source_mode == "pdf":
                args.fdr_pdf = _input_value("FDR PDF path", required=True)
            elif source_mode == "confluence-url":
                args.confluence_url = _input_value("Confluence page URL", required=True)
            else:
                raise RuntimeError("Unsupported FDR source type.")

    cfg = load_config()
    jira = JiraClient(cfg["jira"]["base_url"], cfg["jira"]["email"], cfg["jira"]["api_token"])
    confluence = ConfluenceClient(
        cfg["confluence"]["base_url"],
        cfg["confluence"]["email"],
        cfg["confluence"]["api_token"],
    )

    fdr_text, source_requirement = _load_fdr_text(args, confluence)

    with ThreadPoolExecutor(max_workers=3) as executor:
        fut_code = executor.submit(_discover_local_code, Path("."))
        fut_jira = executor.submit(_discover_jira_context, jira, args.jira_project_key)
        fut_conf = executor.submit(_discover_confluence_context, confluence, args.confluence_url)
        code_ctx = fut_code.result()
        jira_ctx = fut_jira.result()
        conf_ctx = fut_conf.result()

    topics = _split_requirement_topics(fdr_text)
    stories = _build_story_candidates(args.jira_project_key, topics)

    open_questions = _prompt_open_questions() if args.interactive else []
    story_summaries = [s["summary"] for s in stories]

    replacements = {
        "project_name": args.project_name,
        "jira_project_key": args.jira_project_key,
        "source_requirement": source_requirement,
        "prepared_on": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "fdr_summary": fdr_text[:4000] if fdr_text else "No requirement text received.",
        "confluence_findings": _render_list(
            [
                f"Page {item['id']} [{item['space']}]: {item['title']}"
                for item in conf_ctx.get("pages", [])
            ],
            empty="- No Confluence discovery context provided yet.",
        ),
        "jira_findings": _render_issues(jira_ctx.get("issues", [])),
        "codebase_findings": _render_list(
            [
                f"Total files scanned: {code_ctx.get('total_files', 0)}",
                f"Code files scanned: {code_ctx.get('code_files', 0)}",
            ]
        ),
        "frontend_mapping": _render_list(code_ctx.get("categories", {}).get("frontend", [])),
        "backend_mapping": _render_list(code_ctx.get("categories", {}).get("backend", [])),
        "uiux_mapping": _render_list(code_ctx.get("categories", {}).get("uiux", [])),
        "mobile_mapping": _render_list(code_ctx.get("categories", {}).get("mobile", [])),
        "proposed_design": "Draft generated from FDR topics and discovered context. Confirm open questions before ticket creation.",
        "story_breakdown": _render_stories(stories),
        "open_questions": _render_list(open_questions, empty="- No open questions captured yet."),
        "risks_dependencies": "- Dependencies and risks require interactive confirmation with project stakeholders.",
        "implementation_validation_plan": _render_list(
            [
                "Review and approve draft tech spec.",
                "Confirm story split and acceptance criteria.",
                "Create Jira tickets only after user approval.",
            ]
        ),
    }

    jira_plan = {
        "mode": "draft_for_approval",
        "project_name": args.project_name,
        "jira_project_key": args.jira_project_key,
        "stories": stories,
        "notes": [
            "Per policy, Jira issues are not created automatically in this step.",
            "Use these draft stories after user approval.",
        ],
    }

    template_path = Path("templates/tech-spec-v1.md")
    output_path = Path(args.output)
    jira_plan_output = Path(args.jira_plan_output)
    _write_outputs(template_path, output_path, jira_plan_output, replacements, jira_plan)

    result = {
        "status": "ok",
        "project_name": args.project_name,
        "jira_project_key": args.jira_project_key,
        "source_requirement": source_requirement,
        "topics_found": len(topics),
        "stories_drafted": len(story_summaries),
        "tech_spec_output": str(output_path.resolve()),
        "jira_plan_output": str(jira_plan_output.resolve()),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ConfigError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        raise SystemExit(1)
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        raise SystemExit(1)
