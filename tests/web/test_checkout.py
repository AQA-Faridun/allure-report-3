import allure
import pytest
from playwright.sync_api import Page, expect

from intershop.data.catalog import APPLE_WATCH
from intershop.pages.checkout_page import CheckoutPage

pytestmark = [
    pytest.mark.web,
    pytest.mark.regression,
    allure.epic("Checkout"),
    allure.feature("Checkout form"),
    allure.label("owner", "checkout-team"),
    allure.suite("Checkout page"),
]


@allure.story("Access")
@allure.title("Guest has to log in before checkout")
@allure.severity(allure.severity_level.CRITICAL)
def test_guest_must_log_in(page: Page) -> None:
    page.goto(f"/?add-to-cart={APPLE_WATCH.id}")

    checkout = CheckoutPage(page).open()

    expect(checkout.login_required_notice).to_be_visible()
    expect(checkout.place_order_button).to_be_hidden()


@allure.story("Form validation")
@allure.title("Empty billing form shows an error for every required field")
@allure.severity(allure.severity_level.NORMAL)
@allure.tag("negative")
def test_required_billing_fields(logged_in_page: Page) -> None:
    logged_in_page.goto(f"/?add-to-cart={APPLE_WATCH.id}")
    checkout = CheckoutPage(logged_in_page).open()

    checkout.place_order()

    expect(checkout.validation_errors.filter(has_text="обязательное поле")).to_have_count(7)
