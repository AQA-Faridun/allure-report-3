"""Playwright fixtures shared by web, e2e and demo tests (registered as a plugin in tests/conftest.py)."""

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import allure
import pytest
from playwright._impl._api_structures import SetCookieParam
from playwright.sync_api import Browser, BrowserContext, Page, expect

from intershop.api.base_client import create_http_client
from intershop.api.clients.account import AccountClient
from intershop.config import Settings
from intershop.data.factories import Customer
from intershop.utils.attachments import attach_file, attach_html, attach_playwright_trace, attach_text
from tests.fixtures.stash_keys import ALLURE_ENV_KEY, PHASE_REPORTS_KEY


@pytest.fixture(scope="session")
def web_session_setup(browser: Browser, pytestconfig: pytest.Config, settings: Settings) -> None:
    expect.set_options(timeout=settings.ui_timeout_ms)
    pytestconfig.stash[ALLURE_ENV_KEY]["Browser"] = f"{browser.browser_type.name} {browser.version}"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict[str, Any], settings: Settings) -> dict[str, Any]:
    return {
        **browser_context_args,
        "base_url": settings.base_url,
        "locale": "ru-RU",
        "viewport": {"width": 1440, "height": 900},
    }


def _test_failed(request: pytest.FixtureRequest) -> bool:
    reports = request.node.stash.get(PHASE_REPORTS_KEY, {})
    return any(report.failed for report in reports.values())


@pytest.fixture
def context(
    browser: Browser,
    web_session_setup: None,
    browser_context_args: dict[str, Any],
    settings: Settings,
    request: pytest.FixtureRequest,
    tmp_path: Path,
) -> Iterator[BrowserContext]:
    """Replaces the pytest-playwright context to attach artifacts to Allure ourselves.

    Trace, video, HAR, screenshot and page HTML are attached on failure, or always when
    INTERSHOP_WEB_ARTIFACTS=always or the test is an e2e flow.
    """
    har_path = tmp_path / "network.har"
    context = browser.new_context(
        **browser_context_args,
        record_video_dir=tmp_path / "video",
        record_har_path=har_path,
        record_har_content="omit",
    )
    context.set_default_timeout(settings.ui_timeout_ms)
    context.tracing.start(screenshots=True, snapshots=True, sources=False)
    console_lines: list[str] = []
    context.on("console", lambda msg: console_lines.append(f"[{msg.type}] {msg.text}"))

    yield context

    keep_artifacts = (
        _test_failed(request)
        or settings.web_artifacts == "always"
        or request.node.get_closest_marker("e2e") is not None
    )
    if not keep_artifacts:
        context.tracing.stop()
        context.close()
        return

    with allure.step("Browser artifacts"):
        for index, page in enumerate(context.pages, start=1):
            allure.attach(
                page.screenshot(full_page=True),
                name=f"Screenshot #{index}",
                attachment_type=allure.attachment_type.PNG,
            )
            attach_html(f"Page HTML #{index}", page.content())
        trace_path = tmp_path / "trace.zip"
        context.tracing.stop(path=trace_path)
        videos = [page.video for page in context.pages if page.video]
        context.close()

        attach_playwright_trace(trace_path)
        for video in videos:
            attach_file(Path(video.path()), "Video", "video/webm", "webm")
        attach_file(har_path, "Network log (HAR)", "application/json", "har")
        if console_lines:
            attach_text("Browser console", "\n".join(console_lines))


@pytest.fixture
def page(context: BrowserContext) -> Page:
    """The context fixture closes pages itself, after taking screenshots."""
    return context.new_page()


@pytest.fixture
def logged_in_page(
    page: Page, context: BrowserContext, registered_customer: Customer, settings: Settings
) -> Page:
    """A page already logged in as a fresh customer: login goes through HTTP, cookies go to the browser."""
    with (
        allure.step(f"Precondition: log in as '{registered_customer.username}' via HTTP and reuse cookies"),
        create_http_client(settings.base_url, settings.api_timeout_s) as client,
    ):
        response = AccountClient(client).login(registered_customer.username, registered_customer.password)
        assert "Выйти" in response.text, "Login precondition failed"
        context.add_cookies(
            [
                SetCookieParam(
                    name=cookie.name,
                    value=cookie.value or "",
                    domain=cookie.domain,
                    path=cookie.path,
                    secure=cookie.secure,
                    httpOnly=False,
                    sameSite="Lax",
                    expires=float(cookie.expires) if cookie.expires else -1,
                )
                for cookie in client.cookies.jar
            ]
        )
    return page
