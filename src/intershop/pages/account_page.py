import allure
from playwright.sync_api import Page

from intershop.pages.base_page import BasePage


class AccountPage(BasePage):
    path = "/my-account/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        content = page.locator("#content")
        self.username_input = content.get_by_role("textbox", name="Имя пользователя или почта")
        self.password_input = content.get_by_role("textbox", name="Пароль")
        self.login_button = content.get_by_role("button", name="Войти")
        self.account_menu = content.get_by_role("navigation")
        self.greeting = content.get_by_text("Привет")
        self.error = content.locator("ul.woocommerce-error")

    @allure.step("Log in as {username}")
    def login(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    @allure.step("Log out")
    def logout(self) -> None:
        self.account_menu.get_by_role("link", name="Выйти").click()
