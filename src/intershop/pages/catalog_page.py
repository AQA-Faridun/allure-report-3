from typing import Self

import allure
from playwright.sync_api import Page

from intershop.pages.base_page import BasePage
from intershop.pages.components.product_grid import ProductGridComponent


class CatalogPage(BasePage):
    """Shop, category and search result pages share one layout."""

    path = "/shop/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.grid = ProductGridComponent(page)
        self.heading = page.locator("#content").get_by_role("heading", level=1)
        self.result_count = page.locator(".woocommerce-result-count")
        self.sort_select = page.get_by_role("combobox", name="Shop order")
        self.no_results_notice = page.locator("#content .woocommerce-info")

    def open_category(self, category_path: str) -> Self:
        with allure.step(f"Open category /product-category/{category_path}/"):
            self.page.goto(f"/product-category/{category_path}/")
        return self

    @allure.step("Sort catalog by {option}")
    def sort_by(self, option: str) -> None:
        with self.page.expect_navigation():
            self.sort_select.select_option(label=option)
