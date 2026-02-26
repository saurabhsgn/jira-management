from __future__ import annotations


def to_adf(text: str | None) -> dict | None:
    if text is None:
        return None
    if text.strip() == "":
        return {
            "type": "doc",
            "version": 1,
            "content": [],
        }
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": text,
                    }
                ],
            }
        ],
    }


def ensure_list(value: str | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [item.strip() for item in value.split(",") if item.strip()]
