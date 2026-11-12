import allure
import pytest

from intershop.api.clients.wordpress import WordPressClient
from intershop.api.schema import parse_response
from intershop.data.catalog import APPLE_WATCH
from intershop.models.store import ApiError, SearchResult

pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    allure.epic("Platform"),
    allure.label("owner", "platform-team"),
    allure.suite("WordPress REST API"),
]


@allure.feature("REST API surface")
@allure.story("API discovery")
@allure.title("REST index advertises the WooCommerce Store API namespace")
@allure.severity(allure.severity_level.TRIVIAL)
def test_rest_index_exposes_store_namespace(wp_client: WordPressClient) -> None:
    response = wp_client.get_index()

    assert response.status_code == 200
    assert "wc/store" in response.json()["namespaces"]


@allure.feature("REST API surface")
@allure.story("Access control")
@allure.title("WooCommerce REST API v3 requires authentication")
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("negative", "security")
def test_wc_v3_requires_authentication(wp_client: WordPressClient) -> None:
    response = wp_client.list_wc_v3_products()

    assert response.status_code == 401
    assert parse_response(response, ApiError).code == "woocommerce_rest_cannot_view"


@allure.feature("Site search")
@allure.story("Search")
@allure.title("Site-wide search finds a product by name")
@allure.severity(allure.severity_level.MINOR)
def test_site_search_finds_product(wp_client: WordPressClient) -> None:
    response = wp_client.search(APPLE_WATCH.name)

    assert response.status_code == 200
    results = parse_response(response, list[SearchResult])
    assert any(r.title == APPLE_WATCH.name and r.subtype == "product" for r in results)


@allure.feature("REST API surface")
@allure.story("Access control")
@allure.title("User list is not exposed to anonymous visitors")
@allure.issue("SEC-17", "wp/v2/users exposes user logins")
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("security", "known-issue")
@pytest.mark.xfail(reason="SEC-17: the stand exposes /wp-json/wp/v2/users to guests", strict=True)
def test_user_list_is_not_public(wp_client: WordPressClient) -> None:
    response = wp_client.list_users()

    assert response.status_code in {401, 403}, f"Anonymous user list returned {len(response.json())} users"
