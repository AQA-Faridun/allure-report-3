import allure
import pytest
from playwright.sync_api import Page, expect

from intershop.api.clients.products import ProductsClient
from intershop.api.schema import parse_response
from intershop.data.catalog import APPLE_WATCH
from intershop.models.store import Product
from intershop.pages.product_page import ProductPage

pytestmark = [
    pytest.mark.web,
    pytest.mark.regression,
    allure.epic("Catalog"),
    allure.feature("Product page"),
    allure.label("owner", "web-team"),
    allure.suite("Product page"),
]


@allure.story("Product details")
@allure.title("Product page shows the same name and price as the API")
@allure.severity(allure.severity_level.CRITICAL)
@allure.testcase("CAT-110")
def test_product_page_matches_api(page: Page, products_client: ProductsClient) -> None:
    api_product = parse_response(products_client.get_product(APPLE_WATCH.id), Product)

    product_page = ProductPage(page).open_by_slug(APPLE_WATCH.slug)

    expect(product_page.title).to_have_text(api_product.name)
    assert product_page.current_price() == api_product.prices.price_value


@pytest.mark.smoke
@allure.story("Add to cart")
@allure.title("Adding a product shows a confirmation and updates the mini-cart")
@allure.severity(allure.severity_level.BLOCKER)
def test_add_to_cart_from_product_page(page: Page) -> None:
    product_page = ProductPage(page).open_by_slug(APPLE_WATCH.slug)
    price_text = product_page.price.locator("ins").inner_text()

    product_page.add_to_cart()

    expect(product_page.alerts).to_contain_text(f"Вы отложили “{APPLE_WATCH.name}” в свою корзину")
    expect(product_page.header.cart_link).to_contain_text(price_text)


@allure.story("Product details")
@allure.title("Reviews tab can be opened")
@allure.severity(allure.severity_level.TRIVIAL)
def test_reviews_tab_opens(page: Page) -> None:
    product_page = ProductPage(page).open_by_slug(APPLE_WATCH.slug)

    product_page.reviews_tab.click()

    expect(page.get_by_role("tabpanel", name="Отзывы")).to_be_visible()
