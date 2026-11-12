import re
from decimal import Decimal

import allure
from playwright.sync_api import Locator, Page

from intershop.pages.base_page import BasePage
from intershop.utils.money import parse_rub


class CartPage(BasePage):
    path = "/cart/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        content = page.locator("#content")
        self.rows = content.locator("tr.cart_item")
        self.empty_message = content.locator(".cart-empty")
        self.order_total = content.locator(".order-total td")
        self.coupon_input = content.get_by_role("textbox", name="Купон:")
        self.apply_coupon_button = content.get_by_role("button", name="Применить купон")
        self.update_cart_button = content.get_by_role("button", name="Обновить корзину")
        self.checkout_link = content.get_by_role("link", name=re.compile("перейти к оплате", re.IGNORECASE))

    def row(self, product_name: str) -> Locator:
        return self.rows.filter(has=self.page.get_by_role("link", name=product_name, exact=True))

    @allure.step("Read product names in cart")
    def item_names(self) -> list[str]:
        return [name.strip() for name in self.rows.locator("td.product-name").all_inner_texts()]

    @allure.step("Read cart total")
    def total(self) -> Decimal:
        return parse_rub(self.order_total.inner_text())

    @allure.step("Change quantity of {product_name} to {quantity}")
    def set_quantity(self, product_name: str, quantity: int) -> None:
        self.row(product_name).get_by_role("spinbutton").fill(str(quantity))
        self.update_cart_button.click()

    @allure.step("Remove {product_name} from cart")
    def remove(self, product_name: str) -> None:
        self.row(product_name).get_by_role("link", name="Remove this item").click()

    @allure.step("Apply coupon {code}")
    def apply_coupon(self, code: str) -> None:
        self.coupon_input.fill(code)
        self.apply_coupon_button.click()

    @allure.step("Go to checkout")
    def proceed_to_checkout(self) -> None:
        self.checkout_link.click()
