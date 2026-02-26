from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any

import requests


class ApiError(RuntimeError):
    pass


@dataclass
class ConfluenceClient:
    base_url: str
    email: str
    api_token: str

    @property
    def api_base(self) -> str:
        return f"{self.base_url.rstrip('/')}/rest/api"

    def _auth_header(self) -> str:
        token = f"{self.email}:{self.api_token}".encode("utf-8")
        return "Basic " + base64.b64encode(token).decode("utf-8")

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self.api_base}{path}"
        headers = kwargs.pop("headers", {})
        headers.setdefault("Authorization", self._auth_header())
        headers.setdefault("Accept", "application/json")
        if "json" in kwargs:
            headers.setdefault("Content-Type", "application/json")
        response = requests.request(method, url, headers=headers, timeout=30, **kwargs)
        if response.status_code >= 400:
            raise ApiError(f"Confluence API error {response.status_code}: {response.text}")
        return response
