from decimal import Decimal
from typing import Self

import allure
from playwright.sync_api import Page

from intershop.pages.base_page import BasePage
from intershop.utils.money import parse_rub


class ProductPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        summary = page.locator("#content .summary")
        self.title = summary.get_by_role("heading", level=1)
        self.price = summary.locator(".price")
        self.quantity = summary.get_by_role("spinbutton")
        self.add_to_cart_button = summary.get_by_role("button", name="В корзину")
        self.description_tab = page.get_by_role("tab", name="Описание")
        self.reviews_tab = page.get_by_role("tab", name="Отзывы")

    def open_by_slug(self, slug: str) -> Self:
        with allure.step(f"Open product page /product/{slug}/"):
            self.page.goto(f"/product/{slug}/")
        return self

    @allure.step("Read current product price")
    def current_price(self) -> Decimal:
        full_text = self.price.inner_text()  # auto-waits for the price, so count() below sees the final DOM
        sale_price = self.price.locator("ins")
        return parse_rub(sale_price.inner_text() if sale_price.count() else full_text)

    @allure.step("Add product to cart, quantity {quantity}")
    def add_to_cart(self, quantity: int = 1) -> None:
        self.quantity.fill(str(quantity))
        self.add_to_cart_button.click()
