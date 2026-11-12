import re

import allure
import pytest
from playwright.sync_api import Page, expect

from intershop.data.factories import Customer
from intershop.pages.account_page import AccountPage
from intershop.pages.register_page import RegisterPage

pytestmark = [
    pytest.mark.web,
    pytest.mark.regression,
    allure.epic("Customer account"),
    allure.label("owner", "account-team"),
    allure.suite("Account pages"),
]


@allure.feature("Login")
class TestLogin:
    @pytest.mark.smoke
    @allure.story("Valid credentials")
    @allure.title("Customer can log in and log out")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.testcase("ACC-310")
    def test_login_and_logout(self, page: Page, registered_customer: Customer) -> None:
        account = AccountPage(page).open()

        account.login(registered_customer.username, registered_customer.password)
        expect(account.greeting).to_contain_text(registered_customer.username)
        account.logout()

        expect(account.login_button).to_be_visible()

    @allure.story("Invalid credentials")
    @allure.title("Unknown username shows an error")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("negative")
    def test_unknown_user_is_rejected(self, page: Page, new_customer: Customer) -> None:
        account = AccountPage(page).open()

        account.login(new_customer.username, new_customer.password)

        expect(account.error).to_contain_text("Неизвестное имя пользователя")


@allure.feature("Registration")
class TestRegistration:
    @allure.story("Successful registration")
    @allure.title("New customer registers through the form")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_new_customer(self, page: Page, new_customer: Customer) -> None:
        register = RegisterPage(page).open()

        register.register(new_customer)

        expect(register.success_message).to_be_visible()

    @allure.story("Form validation")
    @allure.title("Registration is rejected: {case}")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negative")
    @pytest.mark.parametrize(
        ("case", "username", "email", "expected_error"),
        [
            ("empty username", "", "qa-empty@ex.io", "введите корректное имя пользователя"),
            (
                "email longer than 20 chars",
                "qa_long_email",
                "a" * 15 + "@ex.io",
                "Максимальное допустимое количество символов: 20",
            ),
        ],
        ids=["empty-username", "long-email"],
    )
    def test_registration_validation(
        self, page: Page, new_customer: Customer, case: str, username: str, email: str, expected_error: str
    ) -> None:
        register = RegisterPage(page).open()

        register.register(Customer(username=username, email=email, password=new_customer.password))

        expect(register.error).to_contain_text(expected_error)
        expect(register.success_message).to_be_hidden()

    @allure.story("Form validation")
    @allure.title("Browser blocks a malformed email before the form is sent")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("negative")
    def test_malformed_email_is_blocked_by_browser(self, page: Page, new_customer: Customer) -> None:
        register = RegisterPage(page).open()

        register.register(
            Customer(username=new_customer.username, email="not-an-email", password=new_customer.password)
        )

        is_valid = register.email_input.evaluate("input => input.validity.valid")
        assert is_valid is False
        expect(page).to_have_url(re.compile("/register/$"))
        expect(register.success_message).to_be_hidden()
