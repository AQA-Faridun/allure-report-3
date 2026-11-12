import allure
import pytest
from playwright.sync_api import Page, expect

from intershop.data.catalog import APPLE_WATCH, IPAD_2020
from intershop.pages.base_page import BasePage
from intershop.pages.catalog_page import CatalogPage

pytestmark = [
    pytest.mark.web,
    pytest.mark.regression,
    allure.epic("Catalog"),
    allure.feature("Search"),
    allure.label("owner", "web-team"),
    allure.suite("Product search"),
]


@allure.story("Search results")
@allure.title("Searching '{query}' from the header shows '{expected_name}'")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize(
    ("query", "expected_name"),
    [("apple", APPLE_WATCH.name), ("ipad", IPAD_2020.name)],
    ids=["apple", "ipad"],
)
def test_search_finds_product(page: Page, query: str, expected_name: str) -> None:
    home = BasePage(page).open()

    home.header.search(query)

    results = CatalogPage(page)
    expect(results.heading).to_contain_text(query)
    expect(results.grid.tile(expected_name)).to_be_visible()


@allure.story("Search results")
@allure.title("Search without matches shows a 'nothing found' notice")
@allure.severity(allure.severity_level.MINOR)
@allure.tag("negative")
def test_search_without_results(page: Page) -> None:
    home = BasePage(page).open()

    home.header.search("zzz-no-such-product-zzz")

    results = CatalogPage(page)
    expect(results.no_results_notice).to_be_visible()
    expect(results.grid.tiles).to_have_count(0)
