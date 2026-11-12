import allure
import pytest
from playwright.sync_api import Page, expect

from intershop.data.catalog import APPLE_WATCH, KnownProduct
from intershop.pages.cart_page import CartPage

pytestmark = [
    pytest.mark.web,
    pytest.mark.regression,
    allure.epic("Cart"),
    allure.feature("Cart page"),
    allure.label("owner", "checkout-team"),
    allure.suite("Cart page"),
]


def put_in_cart(page: Page, product: KnownProduct) -> None:
    with allure.step(f"Precondition: put '{product.name}' in the cart"):
        page.goto(f"/?add-to-cart={product.id}")


@allure.story("Empty cart")
@allure.title("Empty cart shows an empty-cart message")
@allure.severity(allure.severity_level.MINOR)
def test_empty_cart_message(page: Page) -> None:
    cart = CartPage(page).open()

    expect(cart.empty_message).to_be_visible()
    expect(cart.rows).to_have_count(0)


@allure.story("Quantity")
@allure.title("Changing quantity to {quantity} recalculates the total")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("quantity", [2, 4])
def test_change_quantity_recalculates_total(page: Page, quantity: int) -> None:
    put_in_cart(page, APPLE_WATCH)
    cart = CartPage(page).open()
    unit_total = cart.total()

    cart.set_quantity(APPLE_WATCH.name, quantity)

    expect(cart.alerts).to_contain_text("Cart updated.")
    assert cart.total() == unit_total * quantity


@allure.story("Remove item")
@allure.title("Removing the only product empties the cart")
@allure.severity(allure.severity_level.NORMAL)
def test_remove_product(page: Page) -> None:
    put_in_cart(page, APPLE_WATCH)
    cart = CartPage(page).open()

    cart.remove(APPLE_WATCH.name)

    expect(cart.empty_message).to_be_visible()


@allure.story("Coupons")
@allure.title("Unknown coupon is rejected with an error")
@allure.severity(allure.severity_level.NORMAL)
@allure.tag("negative")
def test_unknown_coupon_is_rejected(page: Page) -> None:
    put_in_cart(page, APPLE_WATCH)
    cart = CartPage(page).open()

    cart.apply_coupon("NO-SUCH-COUPON")

    expect(cart.alerts).to_contain_text("Неверный купон.")
