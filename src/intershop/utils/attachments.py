"""Allure attachment helpers, including Allure 3 specific content types."""

import json
import shlex
import time
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl

import allure
import httpx

HTTP_EXCHANGE_MIME = "application/vnd.allure.http+json"
PLAYWRIGHT_TRACE_MIME = "application/vnd.allure.playwright-trace"
MERMAID_MIME = "application/vnd.allure.diagrams.mermaid"

_REDACTED_HEADERS = frozenset({"authorization", "cookie", "set-cookie", "x-wc-store-api-nonce"})


def attach_json(name: str, data: Any) -> None:
    allure.attach(
        json.dumps(data, ensure_ascii=False, indent=2, default=str),
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )


def attach_text(name: str, text: str) -> None:
    allure.attach(text, name=name, attachment_type=allure.attachment_type.TEXT)


def attach_html(name: str, html: str) -> None:
    allure.attach(html, name=name, attachment_type=allure.attachment_type.HTML)


def attach_mermaid(name: str, diagram: str) -> None:
    allure.attach(diagram, name=name, attachment_type=MERMAID_MIME, extension="mmd")


def attach_file(path: Path, name: str, mime_type: str, extension: str) -> None:
    allure.attach.file(str(path), name=name, attachment_type=mime_type, extension=extension)


def attach_playwright_trace(path: Path) -> None:
    """Allure 3 opens this content type in the embedded Playwright Trace Viewer."""
    attach_file(path, "Playwright trace", PLAYWRIGHT_TRACE_MIME, "zip")


def attach_http_exchange(response: httpx.Response, started_at_ms: int) -> None:
    """Attach request/response in the Allure 3 HTTP exchange format and as a curl command."""
    exchange = {
        "schemaVersion": 1,
        "start": started_at_ms,
        "stop": int(time.time() * 1000),
        "request": _request_payload(response.request),
        "response": _response_payload(response),
    }
    title = f"{response.request.method} {response.request.url.path} → {response.status_code}"
    allure.attach(
        json.dumps(exchange, ensure_ascii=False),
        name=title,
        attachment_type=HTTP_EXCHANGE_MIME,
        extension="httpexchange",
    )
    attach_text("curl", to_curl(response.request))


def to_curl(request: httpx.Request) -> str:
    parts = ["curl", "-X", request.method, shlex.quote(str(request.url))]
    for name, value in request.headers.items():
        shown = "***" if name.lower() in _REDACTED_HEADERS else value
        parts += ["-H", shlex.quote(f"{name}: {shown}")]
    if request.content:
        parts += ["--data-raw", shlex.quote(request.content.decode(errors="replace"))]
    return " ".join(parts)


def _headers(headers: httpx.Headers) -> list[dict[str, str]]:
    return [
        {"name": name, "value": "***" if name.lower() in _REDACTED_HEADERS else value}
        for name, value in headers.multi_items()
    ]


def _body(content: bytes, content_type: str | None) -> dict[str, Any]:
    body: dict[str, Any] = {
        "encoding": "utf8",
        "value": content.decode(errors="replace"),
        "size": len(content),
    }
    if content_type:
        body["contentType"] = content_type
    if content_type and content_type.startswith("application/x-www-form-urlencoded"):
        body["form"] = [{"name": k, "value": v} for k, v in parse_qsl(body["value"])]
    return body


def _request_payload(request: httpx.Request) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "method": request.method,
        "url": str(request.url),
        "headers": _headers(request.headers),
    }
    if request.url.params:
        payload["query"] = [{"name": k, "value": v} for k, v in request.url.params.multi_items()]
    if request.content:
        payload["body"] = _body(request.content, request.headers.get("content-type"))
    return payload


def _response_payload(response: httpx.Response) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": response.status_code,
        "statusText": response.reason_phrase,
        "headers": _headers(response.headers),
    }
    if response.content:
        payload["body"] = _body(response.content, response.headers.get("content-type"))
    return payload
