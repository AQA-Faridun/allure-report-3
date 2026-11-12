import platform
from collections.abc import Generator, Iterator
from pathlib import Path

import allure
import httpx
import pytest

from intershop.api.base_client import create_http_client
from intershop.api.clients.account import AccountClient
from intershop.api.clients.cart import CartClient
from intershop.api.clients.products import ProductsClient
from intershop.api.clients.site import SiteClient
from intershop.api.clients.wordpress import WordPressClient
from intershop.config import Settings, get_settings
from intershop.data.factories import BillingAddressFactory, Customer, CustomerFactory
from tests.fixtures.stash_keys import ALLURE_ENV_KEY, PHASE_REPORTS_KEY

pytest_plugins = ["tests.fixtures.web"]


LAYER_BY_MARKER = {"e2e": "e2e", "web": "web", "api": "api"}
PARENT_SUITE_BY_LAYER = {"api": "API", "web": "Web UI", "e2e": "End-to-end"}


# --- Hooks -------------------------------------------------------------------------------------------


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    """Keep setup/call/teardown reports on the item so fixtures can react to a failed test."""
    report = yield
    item.stash.setdefault(PHASE_REPORTS_KEY, {})[report.when] = report
    return report


def pytest_configure(config: pytest.Config) -> None:
    settings = get_settings()
    config.stash[ALLURE_ENV_KEY] = {
        "Stand": settings.stand_name,
        "Base URL": settings.base_url,
        "Python": platform.python_version(),
        "OS": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "pytest": pytest.__version__,
        "httpx": httpx.__version__,
    }


def pytest_testnodedown(node: object, error: object) -> None:
    """xdist controller: merge environment facts collected by workers (e.g. browser version)."""
    worker_env = getattr(node, "workeroutput", {}).get("allure_env", {})
    config: pytest.Config = node.config  # type: ignore[attr-defined]
    config.stash[ALLURE_ENV_KEY].update(worker_env)


def pytest_sessionfinish(session: pytest.Session) -> None:
    config = session.config
    if hasattr(config, "workerinput"):
        config.workeroutput["allure_env"] = config.stash[ALLURE_ENV_KEY]  # type: ignore[attr-defined]
        return
    alluredir = config.getoption("allure_report_dir", None)
    if not alluredir:
        return
    lines = [f"{key}={value}" for key, value in sorted(config.stash[ALLURE_ENV_KEY].items())]
    (Path(alluredir) / "environment.properties").write_text("\n".join(lines) + "\n", encoding="utf-8")


# --- Allure labels shared by every test --------------------------------------------------------------


@pytest.fixture(autouse=True)
def _allure_layer_labels(request: pytest.FixtureRequest) -> None:
    """Set `layer` (drives the Testing pyramid chart) and `parent_suite` from pytest markers."""
    for marker, layer in LAYER_BY_MARKER.items():
        if request.node.get_closest_marker(marker):
            allure.dynamic.label("layer", layer)
            allure.dynamic.parent_suite(PARENT_SUITE_BY_LAYER[layer])
            break


# --- Settings, data, shared clients ------------------------------------------------------------------


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture
def http_client(settings: Settings) -> Iterator[httpx.Client]:
    """Fresh client per test: its own cookie jar means its own WooCommerce session and cart."""
    with create_http_client(settings.base_url, settings.api_timeout_s) as client:
        yield client


@pytest.fixture
def products_client(http_client: httpx.Client) -> ProductsClient:
    return ProductsClient(http_client)


@pytest.fixture
def cart_client(http_client: httpx.Client) -> CartClient:
    return CartClient(http_client)


@pytest.fixture
def wp_client(http_client: httpx.Client) -> WordPressClient:
    return WordPressClient(http_client)


@pytest.fixture
def account_client(http_client: httpx.Client) -> AccountClient:
    return AccountClient(http_client)


@pytest.fixture
def site_client(http_client: httpx.Client) -> SiteClient:
    return SiteClient(http_client)


@pytest.fixture(scope="session")
def customer_factory(settings: Settings) -> CustomerFactory:
    return CustomerFactory(settings.data_seed)


@pytest.fixture(scope="session")
def billing_factory(settings: Settings) -> BillingAddressFactory:
    return BillingAddressFactory(settings.data_seed)


@pytest.fixture
def new_customer(customer_factory: CustomerFactory) -> Customer:
    """A customer that does not exist on the site yet."""
    return customer_factory.build()


@pytest.fixture
def registered_customer(new_customer: Customer, settings: Settings) -> Customer:
    """A customer registered through the site form before the test.

    The shop has no API to delete accounts, so customers stay on the stand; unique generated
    names keep tests independent anyway.
    """
    with (
        allure.step(f"Precondition: register customer '{new_customer.username}'"),
        create_http_client(settings.base_url, settings.api_timeout_s) as client,
    ):
        response = AccountClient(client).register(new_customer)
        assert "Регистрация завершена" in response.text, "Customer registration precondition failed"
    return new_customer
