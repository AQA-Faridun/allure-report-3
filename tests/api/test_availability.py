import allure
import pytest

from intershop.api.clients.cart import CartClient
from intershop.api.clients.products import ProductsClient
from intershop.api.clients.site import SiteClient
from intershop.api.clients.wordpress import WordPressClient
from intershop.pages.account_page import AccountPage
from intershop.pages.base_page import BasePage
from intershop.pages.cart_page import CartPage
from intershop.pages.catalog_page import CatalogPage
from intershop.pages.register_page import RegisterPage

pytestmark = [
    pytest.mark.api,
    pytest.mark.smoke,
    allure.epic("Platform"),
    allure.feature("Availability"),
    allure.suite("Stand availability"),
    allure.label("owner", "platform-team"),
    allure.tag("smoke"),
]


@allure.story("REST API endpoints")
@allure.title("REST API index is available")
@allure.severity(allure.severity_level.CRITICAL)
def test_rest_index_is_available(wp_client: WordPressClient) -> None:
    response = wp_client.get_index()

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")


@allure.story("REST API endpoints")
@allure.title("Store API products endpoint is available")
@allure.severity(allure.severity_level.CRITICAL)
def test_products_endpoint_is_available(products_client: ProductsClient) -> None:
    response = products_client.list_products()

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")


@allure.story("REST API endpoints")
@allure.title("Store API categories endpoint is available")
@allure.severity(allure.severity_level.NORMAL)
def test_categories_endpoint_is_available(products_client: ProductsClient) -> None:
    response = products_client.list_categories()

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")


@allure.story("REST API endpoints")
@allure.title("Store API reviews endpoint is available")
@allure.severity(allure.severity_level.MINOR)
def test_reviews_endpoint_is_available(products_client: ProductsClient) -> None:
    response = products_client.list_reviews()

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")


@allure.story("REST API endpoints")
@allure.title("Store API cart endpoint is available")
@allure.severity(allure.severity_level.CRITICAL)
def test_cart_endpoint_is_available(cart_client: CartClient) -> None:
    response = cart_client.get_cart()

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")


@allure.story("Storefront pages")
@allure.title("Storefront page {path} is available")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.parametrize(
    "path",
    [BasePage.path, CatalogPage.path, CartPage.path, AccountPage.path, RegisterPage.path],
    ids=["home", "shop", "cart", "my-account", "register"],
)
def test_storefront_page_is_available(site_client: SiteClient, path: str) -> None:
    response = site_client.open_page(path)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
