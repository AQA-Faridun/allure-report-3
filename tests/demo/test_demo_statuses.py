"""Intentionally red tests: they exist only to show every Allure status and artifact.

Excluded from the default run by `-m "not demo_failures"` in pyproject.toml.
Run them with: uv run pytest -m demo_failures
They carry no `api`/`web` markers on purpose, so `-m api` or `-m web` never picks them up.
"""

import sys
from collections import Counter

import allure
import httpx
import pytest
from playwright.sync_api import Page, expect

from intershop.api.clients.products import ProductsClient
from intershop.api.clients.wordpress import WordPressClient
from intershop.api.schema import parse_response
from intershop.data.catalog import APPLE_WATCH
from intershop.models.store import Product
from intershop.pages.product_page import ProductPage

pytestmark = [
    pytest.mark.demo_failures,
    allure.epic("Allure demo"),
    allure.parent_suite("Demo: statuses"),
    allure.label("owner", "qa-showcase"),
    allure.tag("demo"),
]

_attempts: Counter[str] = Counter()


@pytest.fixture
def unreachable_service() -> httpx.Response:
    """Setup that crashes with a network error, so the test becomes broken before it starts."""
    with httpx.Client(timeout=1) as client:
        return client.get("http://127.0.0.1:9/health")


@allure.feature("Failed")
@allure.story("Product defect")
@allure.label("layer", "api")
@allure.title("[failed] API price differs from the price in the 'pricing service'")
@allure.issue("DEMO-1", "Price mismatch between catalog and pricing")
@allure.severity(allure.severity_level.CRITICAL)
def test_demo_failed_assertion(products_client: ProductsClient) -> None:
    expected_price_from_pricing_service = 1

    product = parse_response(products_client.get_product(APPLE_WATCH.id), Product)

    assert product.prices.price_value == expected_price_from_pricing_service


@allure.feature("Broken")
@allure.story("Test defect")
@allure.label("layer", "api")
@allure.title("[broken] Test code reads a field the API never returns")
@allure.severity(allure.severity_level.NORMAL)
def test_demo_broken_by_test_code(products_client: ProductsClient) -> None:
    product_json = products_client.get_product(APPLE_WATCH.id).json()

    assert product_json["stock_quantity"] > 0


@allure.feature("Broken")
@allure.story("Environment defect")
@allure.label("layer", "api")
@allure.title("[broken] Precondition fails: dependent service is unreachable")
@allure.severity(allure.severity_level.MINOR)
def test_demo_broken_in_setup(unreachable_service: httpx.Response) -> None:
    assert unreachable_service.status_code == 200


@allure.feature("Failed")
@allure.story("UI defect")
@allure.label("layer", "web")
@allure.title("[failed] Product page heading check fails: screenshot, trace, video and HAR are attached")
@allure.severity(allure.severity_level.BLOCKER)
@allure.issue("DEMO-2", "Product title renamed")
def test_demo_web_failure(page: Page) -> None:
    product_page = ProductPage(page).open_by_slug(APPLE_WATCH.slug)

    expect(product_page.title).to_have_text("Apple Watch Ultra 3", timeout=3_000)


@allure.feature("Flaky")
@allure.story("Retries")
@allure.label("layer", "api")
@allure.title("[flaky] Fails on the first attempt and passes on rerun")
@allure.description(
    "pytest-rerunfailures reruns the test; Allure 3 shows earlier attempts on the **Retries** tab "
    "and marks the test as flaky."
)
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.flaky(reruns=2)
def test_demo_flaky_passes_on_retry(request: pytest.FixtureRequest, products_client: ProductsClient) -> None:
    _attempts[request.node.nodeid] += 1
    response = products_client.list_products(per_page=1)

    assert response.status_code == 200
    assert _attempts[request.node.nodeid] > 1, "Simulated flaky failure on the first attempt"


@allure.feature("Failed")
@allure.story("Fixed bug")
@allure.label("layer", "api")
@allure.title("[failed] XPASS(strict): a known bug was fixed, so the xfail mark must go")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.xfail(reason="DEMO-3: catalog was empty last sprint", strict=True)
def test_demo_strict_xpass(products_client: ProductsClient) -> None:
    assert parse_response(products_client.list_products(per_page=1), list[Product])


@allure.feature("Known issues")
@allure.story("Security")
@allure.label("layer", "api")
@allure.title("[known issue] User list is public")
@allure.issue("SEC-17", "wp/v2/users exposes user logins")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description(
    "Fails for real. Its historyId is listed in `allure/known-issues.json`, so Allure 3 shows it "
    "as a known issue and the quality gate does not count it."
)
def test_demo_known_issue(wp_client: WordPressClient) -> None:
    response = wp_client.list_users()

    assert response.status_code in {401, 403}, "SEC-17: anonymous visitors can list site users"


@allure.feature("Skipped")
@allure.story("Skip")
@allure.label("layer", "api")
@allure.title("[skipped] Feature is not deployed to this stand")
@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.skip(reason="Wishlist is not deployed on intershop6")
def test_demo_skipped() -> None:
    pass


@allure.feature("Skipped")
@allure.story("Conditional skip")
@allure.label("layer", "web")
@allure.title("[skipped] Windows-only check is skipped on other platforms")
@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.skipif(sys.platform != "win32", reason="Runs only on Windows agents")
def test_demo_skipped_by_platform() -> None:
    pass
