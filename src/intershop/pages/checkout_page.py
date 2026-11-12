import allure
from playwright.sync_api import Locator, Page

from intershop.data.factories import BillingAddress
from intershop.pages.base_page import BasePage


class CheckoutPage(BasePage):
    path = "/checkout/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        content = page.locator("#content")
        self.login_required_notice = content.get_by_text("Для оформления заказа необходимо авторизоваться")
        self.place_order_button = content.get_by_role("button", name="Оформить заказ")
        self.validation_errors = content.locator("ul.woocommerce-error > li")
        self.order_review = content.locator("#order_review")

    def _field(self, label: str) -> Locator:
        return self.page.get_by_role("textbox", name=f"{label} *", exact=True)

    def fill_billing(self, address: BillingAddress) -> None:
        with allure.step(f"Fill billing details for {address.first_name} {address.last_name}"):
            self._field("Имя").fill(address.first_name)
            self._field("Фамилия").fill(address.last_name)
            self._field("Адрес").fill(address.street)
            self._field("Город / Населенный пункт").fill(address.city)
            self._field("Область").fill(address.region)
            self._field("Почтовый индекс").fill(address.postcode)
            self._field("Телефон").fill(address.phone)

    @allure.step("Select payment method {method}")
    def select_payment(self, method: str) -> None:
        self.page.get_by_role("radio", name=method).check()

    @allure.step("Place order")
    def place_order(self) -> None:
        self.place_order_button.click()
