import allure
import pytest

from intershop.api.clients.account import AccountClient
from intershop.data.factories import Customer, CustomerFactory

pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    allure.epic("Customer account"),
    allure.label("owner", "account-team"),
    allure.suite("Account forms over HTTP"),
]


@allure.feature("Registration")
class TestRegistrationApi:
    @pytest.mark.smoke
    @allure.story("Successful registration")
    @allure.title("New customer can register and is logged in right away")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.testcase("ACC-301")
    def test_register_logs_customer_in(self, account_client: AccountClient, new_customer: Customer) -> None:
        register_response = account_client.register(new_customer)
        account_response = account_client.open_account_page()

        assert "Регистрация завершена" in register_response.text
        assert "Выйти" in account_response.text, "Logout link is shown only to a logged-in customer"

    @allure.story("Duplicate registration")
    @allure.title("Registering a taken {taken_field} is rejected")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negative")
    @pytest.mark.parametrize(
        ("taken_field", "expected_error"),
        [
            ("username", "Учетная запись с таким именем пользователя уже зарегистрирована"),
            ("email", "Учетная запись с такой почтой уже"),
        ],
        ids=["username", "email"],
    )
    def test_duplicate_registration_is_rejected(
        self,
        account_client: AccountClient,
        registered_customer: Customer,
        customer_factory: CustomerFactory,
        taken_field: str,
        expected_error: str,
    ) -> None:
        other = customer_factory.build()
        duplicate = Customer(
            username=registered_customer.username if taken_field == "username" else other.username,
            email=registered_customer.email if taken_field == "email" else other.email,
            password=other.password,
        )

        response = account_client.register(duplicate)

        assert expected_error in AccountClient.error_text(response.text)


@allure.feature("Login")
@allure.story("Valid credentials")
@allure.title("Registered customer can log in by {login_field}")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.parametrize("login_field", ["username", "email"])
def test_login_with_valid_credentials(
    account_client: AccountClient, registered_customer: Customer, login_field: str
) -> None:
    login = registered_customer.username if login_field == "username" else registered_customer.email

    response = account_client.login(login, registered_customer.password)

    assert "Выйти" in response.text, "Logout link is shown only to a logged-in customer"
    assert AccountClient.error_text(response.text) == ""


@allure.feature("Login")
@allure.story("Invalid credentials")
@allure.title("Login with a wrong password is rejected")
@allure.severity(allure.severity_level.NORMAL)
@allure.tag("negative")
def test_login_with_wrong_password(account_client: AccountClient, registered_customer: Customer) -> None:
    response = account_client.login(registered_customer.username, "definitely-wrong-password")

    assert "неверный" in AccountClient.error_text(response.text)
    assert "Выйти" not in response.text
