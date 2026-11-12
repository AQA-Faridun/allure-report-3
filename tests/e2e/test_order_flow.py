import allure
import pytest
from playwright.sync_api import Page, expect

from intershop.data.catalog import APPLE_WATCH
from intershop.data.factories import BillingAddressFactory, Customer
from intershop.pages.cart_page import CartPage
from intershop.pages.catalog_page import CatalogPage
from intershop.pages.checkout_page import CheckoutPage
from intershop.pages.order_received_page import OrderReceivedPage
from intershop.pages.product_page import ProductPage
from intershop.pages.register_page import RegisterPage
from intershop.utils.attachments import attach_mermaid

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.web,
    pytest.mark.regression,
    allure.epic("Checkout"),
    allure.feature("Order placement"),
    allure.label("owner", "checkout-team"),
    allure.suite("Order flow"),
    # The public stand sometimes answers slowly; one retry is shown as a retry in Allure.
    pytest.mark.flaky(reruns=1, reruns_delay=5),
]

ORDER_FLOW_DIAGRAM = """flowchart LR
    A[Search] --> B[Product page] --> C[Cart] --> D[Checkout] --> E[Order received]
"""


@pytest.mark.smoke
@allure.story("Logged-in customer")
@allure.title("Customer finds a product, buys {quantity} item(s) and gets an order number")
@allure.severity(allure.severity_level.BLOCKER)
@allure.testcase("ORD-401")
@allure.description(
    "Main business flow: **search → product page → cart → checkout → order received**.\n\n"
    "The customer is registered and logged in through HTTP before the test to keep the UI part focused."
)
@pytest.mark.parametrize("quantity", [2])
def test_customer_places_order(
    logged_in_page: Page, billing_factory: BillingAddressFactory, quantity: int
) -> None:
    attach_mermaid("Flow under test", ORDER_FLOW_DIAGRAM)
    page = logged_in_page
    billing = billing_factory.build()

    with allure.step("Find the product through search"):
        page.goto("/")
        CatalogPage(page).header.search("apple")
        CatalogPage(page).grid.open_product(APPLE_WATCH.name)

    with allure.step(f"Add {quantity} item(s) to the cart"):
        product_page = ProductPage(page)
        unit_price = product_page.current_price()
        product_page.add_to_cart(quantity)
        expect(product_page.alerts).to_contain_text(APPLE_WATCH.name)

    with allure.step("Check the cart and go to checkout"):
        cart = CartPage(page).open()
        assert cart.item_names() == [APPLE_WATCH.name]
        assert cart.total() == unit_price * quantity
        cart.proceed_to_checkout()

    with allure.step("Fill billing details and place the order"):
        checkout = CheckoutPage(page)
        checkout.fill_billing(billing)
        checkout.select_payment("Оплата при доставке")
        checkout.place_order()

    with allure.step("Check the order confirmation"):
        confirmation = OrderReceivedPage(page)
        expect(confirmation.thank_you).to_be_visible()
        expect(confirmation.payment_method).to_have_text("Оплата при доставке")
        assert confirmation.order_number.inner_text().isdigit()
        assert confirmation.total() == unit_price * quantity
        # excluded=True: the order number changes every run and must not break the test history id.
        allure.dynamic.parameter("order number", confirmation.order_number.inner_text(), excluded=True)


@allure.story("New customer")
@allure.title("New customer registers, adds a product from the shop page and places an order")
@allure.severity(allure.severity_level.CRITICAL)
def test_new_customer_registers_and_orders(
    page: Page, new_customer: Customer, billing_factory: BillingAddressFactory
) -> None:
    with allure.step("Register through the form"):
        register = RegisterPage(page).open()
        register.register(new_customer)
        expect(register.success_message).to_be_visible()

    with allure.step("Add a product from the shop grid"):
        shop = CatalogPage(page).open()
        shop.grid.add_to_cart(APPLE_WATCH.name)
        expect(shop.grid.tile(APPLE_WATCH.name).get_by_role("link", name="Подробнее")).to_be_visible()

    with allure.step("Checkout"):
        checkout = CheckoutPage(page).open()
        checkout.fill_billing(billing_factory.build())
        checkout.place_order()

    expect(OrderReceivedPage(page).heading).to_be_visible()
