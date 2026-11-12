import allure
from playwright.sync_api import Page

from intershop.data.factories import Customer
from intershop.pages.base_page import BasePage


class RegisterPage(BasePage):
    path = "/register/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        content = page.locator("#content")
        self.username_input = content.get_by_role("textbox", name="Имя пользователя")
        self.email_input = content.get_by_role("textbox", name="Адрес почты")
        self.password_input = content.get_by_role("textbox", name="Пароль")
        self.submit_button = content.get_by_role("button", name="Зарегистрироваться")
        self.success_message = content.get_by_text("Регистрация завершена")
        self.error = content.locator("ul.woocommerce-error")

    def register(self, customer: Customer) -> None:
        with allure.step(f"Register as '{customer.username}' <{customer.email}>"):
            self.username_input.fill(customer.username)
            self.email_input.fill(customer.email)
            self.password_input.fill(customer.password)
            self.submit_button.click()
