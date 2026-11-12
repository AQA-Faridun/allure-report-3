import re

import allure
import pytest
from playwright.sync_api import Page, expect

from intershop.pages.base_page import BasePage
from intershop.pages.catalog_page import CatalogPage

pytestmark = [
    pytest.mark.web,
    pytest.mark.regression,
    allure.epic("Catalog"),
    allure.feature("Navigation"),
    allure.label("owner", "web-team"),
    allure.suite("Header and menu"),
]


@pytest.mark.smoke
@allure.story("Header")
@allure.title("Home page shows search, cart and login in the header")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description_html(
    "<p>Checks the header widgets every page relies on:</p>"
    "<ul><li>product search box</li><li>mini-cart link with the cart total</li><li>login link</li></ul>"
)
def test_home_page_header(page: Page) -> None:
    home = BasePage(page).open()

    expect(page).to_have_title(re.compile("Skillbox"))
    expect(home.header.search_box).to_be_visible()
    expect(home.header.cart_link).to_contain_text("₽")
    expect(home.header.login_link).to_be_visible()


@allure.story("Main menu")
@allure.title("Menu item '{item}' opens the '{item}' page")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize("item", ["Корзина", "Мой аккаунт", "Бонусная программа"])
def test_menu_item_opens_page(page: Page, item: str) -> None:
    home = BasePage(page).open()

    home.header.open_menu_item(item)

    expect(page).to_have_title(re.compile(f"^{item}"))


@allure.story("Catalog menu")
@allure.title("Catalog submenu opens a category page")
@allure.severity(allure.severity_level.MINOR)
def test_catalog_submenu_opens_category(page: Page) -> None:
    home = BasePage(page).open()

    home.header.open_category("Электроника")

    expect(CatalogPage(page).heading).to_have_text("Электроника")
    expect(page).to_have_url(re.compile("/product-category/catalog/electronics/"))
