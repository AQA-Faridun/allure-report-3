from decimal import Decimal

import allure
from playwright.sync_api import Page

from intershop.pages.base_page import BasePage
from intershop.utils.money import parse_rub


class OrderReceivedPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        content = page.locator("#content")
        self.heading = content.get_by_role("heading", name="Заказ получен")
        self.thank_you = content.get_by_text("Спасибо! Ваш заказ был получен.")
        self.order_number = content.locator(".woocommerce-order-overview__order strong")
        self.order_total = content.locator(".woocommerce-order-overview__total strong")
        self.payment_method = content.locator(".woocommerce-order-overview__payment-method strong")

    @allure.step("Read order total")
    def total(self) -> Decimal:
        return parse_rub(self.order_total.inner_text())
