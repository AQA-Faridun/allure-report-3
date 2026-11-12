import re

import allure
from playwright.sync_api import Page


class HeaderComponent:
    def __init__(self, page: Page) -> None:
        self._page = page
        banner = page.get_by_role("banner").first
        self.search_box = banner.get_by_role("search").get_by_role("textbox")
        self.cart_link = banner.get_by_role("link", name=re.compile(r"\[.*₽.*\]"))
        self.login_link = banner.get_by_role("link", name="Войти")
        self.menu = banner.get_by_role("navigation")

    @allure.step("Header: search for {query}")
    def search(self, query: str) -> None:
        self.search_box.fill(query)
        self.search_box.press("Enter")

    @allure.step("Header: open menu item {item}")
    def open_menu_item(self, item: str) -> None:
        self.menu.get_by_role("link", name=item, exact=True).first.click()

    @allure.step("Header: open catalog category {category}")
    def open_category(self, category: str) -> None:
        self.menu.get_by_role("link", name="Каталог", exact=True).hover()
        self.menu.get_by_role("link", name=category, exact=True).click()
