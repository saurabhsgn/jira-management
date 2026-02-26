from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from _config import ConfigError, load_config
from _confluence import ConfluenceClient
from _jira import JiraClient
from _utils import ensure_list, to_adf


def _get_clients() -> tuple[JiraClient, ConfluenceClient]:
    cfg = load_config()
    jira_cfg = cfg["jira"]
    confluence_cfg = cfg["confluence"]
    jira = JiraClient(
        base_url=jira_cfg["base_url"],
        email=jira_cfg["email"],
        api_token=jira_cfg["api_token"],
    )
    confluence = ConfluenceClient(
        base_url=confluence_cfg["base_url"],
        email=confluence_cfg["email"],
        api_token=confluence_cfg["api_token"],
    )
    return jira, confluence


def _adf_to_text(node: Any) -> str:
    if isinstance(node, dict):
        if node.get("type") == "text":
            return node.get("text", "")
        return "".join(_adf_to_text(child) for child in node.get("content", []))
    if isinstance(node, list):
        return "".join(_adf_to_text(child) for child in node)
    return ""


def _strip_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)


def _sentences(value: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", value.strip())
    return [p.strip() for p in parts if p.strip()]


def _jira_create_issue(jira: JiraClient, fields: dict[str, Any]) -> dict[str, Any]:
    response = jira.request("POST", "/issue", json={"fields": fields}).json()
    return {
        "issue_key": response.get("key"),
        "issue_id": response.get("id"),
        "self": response.get("self"),
    }


def _jira_update_issue(jira: JiraClient, issue_key: str, fields: dict[str, Any]) -> dict[str, Any]:
    jira.request("PUT", f"/issue/{issue_key}", json={"fields": fields})
    return {"issue_key": issue_key}


def _jira_issue_url(jira: JiraClient, issue_key: str) -> str:
    return f"{jira.base_url.rstrip('/')}/browse/{issue_key}"


def create_jira(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    fields = {
        "project": {"key": args["project_key"]},
        "issuetype": {"name": args["issue_type"]},
        "summary": args["summary"],
    }

    description = args.get("description")
    if description:
        fields["description"] = to_adf(description)

    labels = ensure_list(args.get("labels"))
    if labels:
        fields["labels"] = labels

    components = ensure_list(args.get("components"))
    if components:
        fields["components"] = [{"name": name} for name in components]

    assignee = args.get("assignee")
    if assignee:
        fields["assignee"] = {"accountId": assignee}

    priority = args.get("priority")
    if priority:
        fields["priority"] = {"name": priority}

    result = _jira_create_issue(jira, fields)
    result["issue_url"] = _jira_issue_url(jira, result["issue_key"])
    return result


def create_confluence_page(args: dict[str, Any]) -> dict[str, Any]:
    _, confluence = _get_clients()
    payload = {
        "type": "page",
        "title": args["title"],
        "space": {"key": args["space_key"]},
        "body": {
            "storage": {
                "value": args["body"],
                "representation": args.get("representation") or "storage",
            }
        },
    }
    parent_page_id = args.get("parent_page_id")
    if parent_page_id:
        payload["ancestors"] = [{"id": str(parent_page_id)}]

    response = confluence.request("POST", "/content", json=payload).json()
    return {
        "page_id": response.get("id"),
        "page_url": response.get("_links", {}).get("base", "")
        + response.get("_links", {}).get("webui", ""),
    }


def update_jira_summary(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    return _jira_update_issue(jira, args["issue_key"], {"summary": args["summary"]})


def update_jira_description(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    issue_key = args["issue_key"]
    description = args["description"]
    mode = (args.get("mode") or "replace").lower()

    if mode == "append":
        issue = jira.request("GET", f"/issue/{issue_key}", params={"fields": "description"}).json()
        existing = _adf_to_text(issue.get("fields", {}).get("description"))
        description = (existing + "\n" + description).strip()

    return _jira_update_issue(jira, issue_key, {"description": to_adf(description)})


def update_jira_comments(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    issue_key = args["issue_key"]
    comment_id = args.get("comment_id")
    mode = (args.get("mode") or "add").lower()

    if mode == "update" and comment_id:
        response = jira.request(
            "PUT",
            f"/issue/{issue_key}/comment/{comment_id}",
            json={"body": to_adf(args["comment"])},
        ).json()
    else:
        response = jira.request(
            "POST",
            f"/issue/{issue_key}/comment",
            json={"body": to_adf(args["comment"])},
        ).json()

    return {
        "issue_key": issue_key,
        "comment_id": response.get("id"),
    }


def pull_jira(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    params = {}
    fields = args.get("fields")
    if fields:
        params["fields"] = fields
    include_comments = args.get("include_comments")
    if include_comments:
        params.setdefault("fields", "summary,description,status,assignee,comment")
    response = jira.request("GET", f"/issue/{args['issue_key']}", params=params).json()
    return response


def explain_jira(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    issue = jira.request(
        "GET",
        f"/issue/{args['issue_key']}",
        params={"fields": "summary,description,status,assignee,priority"},
    ).json()
    fields = issue.get("fields", {})
    description = _adf_to_text(fields.get("description"))
    assignee = fields.get("assignee", {}).get("displayName")
    summary = fields.get("summary")
    status = fields.get("status", {}).get("name")
    priority = fields.get("priority", {}).get("name")

    explanation = {
        "summary": summary,
        "status": status,
        "priority": priority,
        "assignee": assignee,
        "description": description,
    }
    return {"issue_key": args["issue_key"], "explanation": explanation}


def create_test_cases_from_jira(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    issue = jira.request(
        "GET",
        f"/issue/{args['issue_key']}",
        params={"fields": "summary,description"},
    ).json()
    summary = issue.get("fields", {}).get("summary")
    description = _adf_to_text(issue.get("fields", {}).get("description"))
    cases = [
        {
            "title": f"Validate {summary}",
            "steps": ["Set up prerequisites.", "Perform the action.", "Verify the result."],
            "expected": "Behavior matches the requirement.",
        }
    ]
    return {"issue_key": args["issue_key"], "test_cases": cases, "source": description}


def create_acceptance_criteria_from_jira(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    issue = jira.request(
        "GET",
        f"/issue/{args['issue_key']}",
        params={"fields": "description"},
    ).json()
    description = _adf_to_text(issue.get("fields", {}).get("description"))
    criteria = [f"- {sentence}" for sentence in _sentences(description)]
    if not criteria:
        criteria = ["- Provide acceptance criteria based on requirements."]
    return {"issue_key": args["issue_key"], "acceptance_criteria": "\n".join(criteria)}


def read_confluence_page(args: dict[str, Any]) -> dict[str, Any]:
    _, confluence = _get_clients()
    fmt = args.get("format") or "storage"
    expand = f"body.{fmt},version,space"
    response = confluence.request("GET", f"/content/{args['page_id']}", params={"expand": expand}).json()
    return response


def create_acceptance_criteria_from_confluence(args: dict[str, Any]) -> dict[str, Any]:
    _, confluence = _get_clients()
    response = confluence.request(
        "GET",
        f"/content/{args['page_id']}",
        params={"expand": "body.storage"},
    ).json()
    storage = response.get("body", {}).get("storage", {}).get("value", "")
    text = _strip_html(storage)
    criteria = [f"- {sentence}" for sentence in _sentences(text)]
    if not criteria:
        criteria = ["- Provide acceptance criteria based on the page content."]
    return {"page_id": args["page_id"], "acceptance_criteria": "\n".join(criteria)}


def create_jira_from_confluence(args: dict[str, Any]) -> dict[str, Any]:
    jira, confluence = _get_clients()
    response = confluence.request(
        "GET",
        f"/content/{args['page_id']}",
        params={"expand": "body.storage"},
    ).json()
    title = response.get("title") or args.get("summary") or "New issue"
    storage = response.get("body", {}).get("storage", {}).get("value", "")
    description_text = _strip_html(storage)

    fields = {
        "project": {"key": args["project_key"]},
        "issuetype": {"name": args["issue_type"]},
        "summary": title,
        "description": to_adf(description_text),
    }
    result = _jira_create_issue(jira, fields)
    result["issue_url"] = _jira_issue_url(jira, result["issue_key"])
    return result


def transition_jira_status(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    issue_key = args["issue_key"]
    transition_id = args.get("transition_id")
    status_name = args.get("status_name")

    if not transition_id and status_name:
        transitions = jira.request("GET", f"/issue/{issue_key}/transitions").json().get("transitions", [])
        for item in transitions:
            if item.get("name", "").lower() == status_name.lower():
                transition_id = item.get("id")
                break

    if not transition_id:
        raise ValueError("transition_id or status_name is required.")

    jira.request("POST", f"/issue/{issue_key}/transitions", json={"transition": {"id": transition_id}})
    return {"issue_key": issue_key, "transition_id": transition_id}


def assign_jira_issue(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    jira.request("PUT", f"/issue/{args['issue_key']}/assignee", json={"accountId": args["assignee"]})
    return {"issue_key": args["issue_key"], "assignee": args["assignee"]}


def add_jira_labels(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    labels = ensure_list(args.get("labels"))
    updates = [{"add": label} for label in labels]
    jira.request("PUT", f"/issue/{args['issue_key']}", json={"update": {"labels": updates}})
    return {"issue_key": args["issue_key"], "labels_added": labels}


def remove_jira_labels(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    labels = ensure_list(args.get("labels"))
    updates = [{"remove": label} for label in labels]
    jira.request("PUT", f"/issue/{args['issue_key']}", json={"update": {"labels": updates}})
    return {"issue_key": args["issue_key"], "labels_removed": labels}


def set_jira_priority(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    return _jira_update_issue(jira, args["issue_key"], {"priority": {"name": args["priority"]}})


def add_jira_attachment(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    file_path = Path(args["file_path"])
    with file_path.open("rb") as handle:
        response = jira.request(
            "POST",
            f"/issue/{args['issue_key']}/attachments",
            headers={"X-Atlassian-Token": "no-check"},
            files={"file": (file_path.name, handle)},
        ).json()
    attachment_id = response[0].get("id") if response else None
    return {"issue_key": args["issue_key"], "attachment_id": attachment_id}


def link_jira_issues(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    payload = {
        "type": {"name": args["link_type"]},
        "inwardIssue": {"key": args["inward_issue_key"]},
        "outwardIssue": {"key": args["outward_issue_key"]},
    }
    jira.request("POST", "/issueLink", json=payload)
    return {"inward_issue_key": args["inward_issue_key"], "outward_issue_key": args["outward_issue_key"]}


def add_jira_watcher(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    jira.request("POST", f"/issue/{args['issue_key']}/watchers", json=args["watcher"])
    return {"issue_key": args["issue_key"], "watcher": args["watcher"]}


def set_jira_due_date(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    return _jira_update_issue(jira, args["issue_key"], {"duedate": args["due_date"]})


def search_jira(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    response = jira.request("POST", "/search", json={"jql": args["jql"], "maxResults": 50}).json()
    return response


def create_jira_subtask(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    fields = {
        "project": {"key": args["parent_issue_key"].split("-")[0]},
        "parent": {"key": args["parent_issue_key"]},
        "issuetype": {"name": args.get("issue_type") or "Sub-task"},
        "summary": args["summary"],
    }
    result = _jira_create_issue(jira, fields)
    result["issue_url"] = _jira_issue_url(jira, result["issue_key"])
    return result


def delete_jira_issue(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    jira.request("DELETE", f"/issue/{args['issue_key']}")
    return {"issue_key": args["issue_key"], "deleted": True}


def update_jira_components(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    components = ensure_list(args.get("components"))
    return _jira_update_issue(
        jira,
        args["issue_key"],
        {"components": [{"name": name} for name in components]},
    )


def add_jira_worklog(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    payload = {"timeSpent": args["time_spent"]}
    comment = args.get("comment")
    if comment:
        payload["comment"] = to_adf(comment)
    response = jira.request("POST", f"/issue/{args['issue_key']}/worklog", json=payload).json()
    return {"issue_key": args["issue_key"], "worklog_id": response.get("id")}


def get_jira_changelog(args: dict[str, Any]) -> dict[str, Any]:
    jira, _ = _get_clients()
    response = jira.request("GET", f"/issue/{args['issue_key']}/changelog").json()
    return response


def update_confluence_page(args: dict[str, Any]) -> dict[str, Any]:
    _, confluence = _get_clients()
    page_id = args["page_id"]
    current = confluence.request(
        "GET",
        f"/content/{page_id}",
        params={"expand": "body.storage,version"},
    ).json()
    version = current.get("version", {}).get("number", 0) + 1
    title = args.get("title") or current.get("title")
    body = args.get("body") or current.get("body", {}).get("storage", {}).get("value", "")

    payload = {
        "id": page_id,
        "type": "page",
        "title": title,
        "version": {"number": version},
        "body": {"storage": {"value": body, "representation": "storage"}},
    }
    response = confluence.request("PUT", f"/content/{page_id}", json=payload).json()
    return {"page_id": response.get("id"), "version": response.get("version", {}).get("number")}


def delete_confluence_page(args: dict[str, Any]) -> dict[str, Any]:
    _, confluence = _get_clients()
    confluence.request("DELETE", f"/content/{args['page_id']}")
    return {"page_id": args["page_id"], "deleted": True}


def search_confluence_pages(args: dict[str, Any]) -> dict[str, Any]:
    _, confluence = _get_clients()
    response = confluence.request("GET", "/content/search", params={"cql": args["cql"], "limit": 25}).json()
    return response


def add_confluence_comment(args: dict[str, Any]) -> dict[str, Any]:
    _, confluence = _get_clients()
    payload = {
        "type": "comment",
        "container": {"id": str(args["page_id"]), "type": "page"},
        "body": {
            "storage": {
                "value": args["comment"],
                "representation": args.get("representation") or "storage",
            }
        },
    }
    response = confluence.request("POST", f"/content/{args['page_id']}/child/comment", json=payload).json()
    return {"page_id": args["page_id"], "comment_id": response.get("id")}


def update_confluence_labels(args: dict[str, Any]) -> dict[str, Any]:
    _, confluence = _get_clients()
    labels = ensure_list(args.get("labels"))
    mode = (args.get("mode") or "add").lower()
    if mode == "remove":
        for label in labels:
            confluence.request("DELETE", f"/content/{args['page_id']}/label", params={"name": label})
        return {"page_id": args["page_id"], "labels_removed": labels}

    payload = [{"prefix": "global", "name": label} for label in labels]
    response = confluence.request("POST", f"/content/{args['page_id']}/label", json=payload).json()
    return {"page_id": args["page_id"], "labels_added": [item.get("name") for item in response]}


def add_confluence_attachment(args: dict[str, Any]) -> dict[str, Any]:
    _, confluence = _get_clients()
    file_path = Path(args["file_path"])
    with file_path.open("rb") as handle:
        response = confluence.request(
            "POST",
            f"/content/{args['page_id']}/child/attachment",
            headers={"X-Atlassian-Token": "no-check"},
            files={"file": (file_path.name, handle)},
        ).json()
    attachment = response.get("results", [{}])[0]
    return {"page_id": args["page_id"], "attachment_id": attachment.get("id")}


def move_confluence_page(args: dict[str, Any]) -> dict[str, Any]:
    _, confluence = _get_clients()
    response = confluence.request(
        "POST",
        f"/content/{args['page_id']}/move",
        params={"position": "append", "targetId": args["new_parent_id"]},
    ).json()
    return {"page_id": response.get("id"), "new_parent_id": args["new_parent_id"]}


def export_confluence_page(args: dict[str, Any]) -> dict[str, Any]:
    _, confluence = _get_clients()
    page_id = args["page_id"]
    response = confluence.request(
        "GET",
        f"/content/{page_id}",
        params={"expand": "body.export_view"},
    ).json()
    html = response.get("body", {}).get("export_view", {}).get("value", "")
    output_path = args.get("output_path") or f"confluence_{page_id}.html"
    Path(output_path).write_text(html, encoding="utf-8")
    return {"page_id": page_id, "output_path": str(Path(output_path).resolve())}


ACTIONS = {
    "create_jira": create_jira,
    "create_confluence_page": create_confluence_page,
    "update_jira_summary": update_jira_summary,
    "update_jira_description": update_jira_description,
    "update_jira_comments": update_jira_comments,
    "pull_jira": pull_jira,
    "explain_jira": explain_jira,
    "create_test_cases_from_jira": create_test_cases_from_jira,
    "create_acceptance_criteria_from_jira": create_acceptance_criteria_from_jira,
    "read_confluence_page": read_confluence_page,
    "create_acceptance_criteria_from_confluence": create_acceptance_criteria_from_confluence,
    "create_jira_from_confluence": create_jira_from_confluence,
    "transition_jira_status": transition_jira_status,
    "assign_jira_issue": assign_jira_issue,
    "add_jira_labels": add_jira_labels,
    "remove_jira_labels": remove_jira_labels,
    "set_jira_priority": set_jira_priority,
    "add_jira_attachment": add_jira_attachment,
    "link_jira_issues": link_jira_issues,
    "add_jira_watcher": add_jira_watcher,
    "set_jira_due_date": set_jira_due_date,
    "search_jira": search_jira,
    "create_jira_subtask": create_jira_subtask,
    "delete_jira_issue": delete_jira_issue,
    "update_jira_components": update_jira_components,
    "add_jira_worklog": add_jira_worklog,
    "get_jira_changelog": get_jira_changelog,
    "update_confluence_page": update_confluence_page,
    "delete_confluence_page": delete_confluence_page,
    "search_confluence_pages": search_confluence_pages,
    "add_confluence_comment": add_confluence_comment,
    "update_confluence_labels": update_confluence_labels,
    "add_confluence_attachment": add_confluence_attachment,
    "move_confluence_page": move_confluence_page,
    "export_confluence_page": export_confluence_page,
}


def run_action(action: str, args: dict[str, Any]) -> dict[str, Any]:
    try:
        handler = ACTIONS[action]
    except KeyError:
        return {"status": "error", "error": f"Unknown action: {action}"}

    try:
        result = handler(args)
        result["status"] = "ok"
        result["action"] = action
        return result
    except ConfigError as exc:
        return {"status": "error", "action": action, "error": str(exc)}
    except Exception as exc:
        return {"status": "error", "action": action, "error": str(exc)}
