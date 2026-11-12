import allure
import pytest
from playwright.sync_api import Page, expect

from intershop.api.clients.products import ProductsClient
from intershop.api.schema import parse_response
from intershop.data.catalog import PHONES_CATEGORY_ID, STORE_PAGE_SIZE
from intershop.models.store import Product
from intershop.pages.catalog_page import CatalogPage

pytestmark = [
    pytest.mark.web,
    pytest.mark.regression,
    allure.epic("Catalog"),
    allure.label("owner", "web-team"),
    allure.suite("Catalog pages"),
]


@allure.feature("Product listing")
@allure.story("Shop page")
@allure.title("Shop page shows the first page of products and the total from the API")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
def test_shop_page_shows_first_page(page: Page, products_client: ProductsClient) -> None:
    total_in_api = int(products_client.list_products(per_page=1).headers["X-WP-Total"])

    shop = CatalogPage(page).open()

    expect(shop.grid.tiles).to_have_count(STORE_PAGE_SIZE)
    expect(shop.result_count).to_contain_text(f"из {total_in_api}")


@allure.feature("Product listing")
@allure.story("Sorting")
@allure.title("Shop page sorted '{option}' shows prices in {direction} order")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize(
    ("option", "direction"),
    [("По возрастанию цены", "ascending"), ("По убыванию цены", "descending")],
    ids=["price-asc", "price-desc"],
)
def test_sort_by_price(page: Page, option: str, direction: str) -> None:
    shop = CatalogPage(page).open()

    shop.sort_by(option)
    prices = shop.grid.prices()

    assert prices == sorted(prices, reverse=direction == "descending")


@allure.feature("Product listing")
@allure.story("Category page")
@allure.title("Phones category page lists the same products as the API")
@allure.severity(allure.severity_level.NORMAL)
def test_category_page_matches_api(page: Page, products_client: ProductsClient) -> None:
    api_names = {
        product.name
        for product in parse_response(
            products_client.list_products(category=PHONES_CATEGORY_ID, per_page=50), list[Product]
        )
    }

    category = CatalogPage(page).open_category("catalog/electronics/phones")

    expect(category.heading).to_have_text("Телефоны")
    assert set(category.grid.titles()) == api_names
