import allure
import pytest

from intershop.api.clients.cart import CartClient
from intershop.api.clients.products import ProductsClient
from intershop.api.schema import parse_response
from intershop.data.catalog import APPLE_WATCH, IPAD_2020, NON_EXISTENT_ID
from intershop.models.store import ApiError, Cart, Product

pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    allure.epic("Cart"),
    allure.feature("Cart API"),
    allure.label("owner", "checkout-team"),
    allure.suite("Cart: Store API + wc-ajax"),
]


@pytest.mark.smoke
@allure.story("Empty cart")
@allure.title("A new session starts with an empty cart")
@allure.severity(allure.severity_level.CRITICAL)
def test_new_session_cart_is_empty(cart_client: CartClient) -> None:
    response = cart_client.get_cart()

    assert response.status_code == 200
    cart = parse_response(response, Cart)
    assert cart.items_count == 0
    assert cart.items == []


@allure.story("Add to cart")
@allure.title("Adding {quantity} x Apple Watch 6 puts it in the cart with the right total")
@allure.severity(allure.severity_level.BLOCKER)
@allure.testcase("CART-201")
@pytest.mark.parametrize("quantity", [1, 3])
def test_add_product_to_cart(cart_client: CartClient, products_client: ProductsClient, quantity: int) -> None:
    product = parse_response(products_client.get_product(APPLE_WATCH.id), Product)

    add_response = cart_client.add_item(product.id, quantity)
    cart = parse_response(cart_client.get_cart(), Cart)

    assert add_response.status_code == 200
    assert "error" not in add_response.json()
    with allure.step("Check cart content and totals"):
        assert [(item.id, item.quantity) for item in cart.items] == [(product.id, quantity)]
        assert cart.items_count == quantity
        assert cart.totals.to_decimal(cart.totals.total_price) == product.prices.price_value * quantity


@allure.story("Add to cart")
@allure.title("Cart total is the sum of all line totals")
@allure.severity(allure.severity_level.CRITICAL)
def test_cart_total_is_sum_of_lines(cart_client: CartClient) -> None:
    cart_client.add_item(APPLE_WATCH.id, 1)
    cart_client.add_item(IPAD_2020.id, 2)

    cart = parse_response(cart_client.get_cart(), Cart)

    assert len(cart.items) == 2
    lines_sum = sum(item.totals.to_decimal(item.totals.line_total) for item in cart.items)
    assert cart.totals.to_decimal(cart.totals.total_price) == lines_sum


@allure.story("Remove from cart")
@allure.title("Removing the only item empties the cart")
@allure.severity(allure.severity_level.CRITICAL)
def test_remove_item_empties_cart(cart_client: CartClient) -> None:
    cart_client.add_item(APPLE_WATCH.id, 1)
    item_key = parse_response(cart_client.get_cart(), Cart).items[0].key

    remove_response = cart_client.remove_item(item_key)
    cart = parse_response(cart_client.get_cart(), Cart)

    assert remove_response.status_code == 200
    assert cart.items_count == 0


@allure.story("Add to cart")
@allure.title("Unknown product cannot be added to the cart")
@allure.severity(allure.severity_level.NORMAL)
@allure.tag("negative")
def test_unknown_product_is_rejected(cart_client: CartClient) -> None:
    response = cart_client.add_item(NON_EXISTENT_ID, 1)
    cart = parse_response(cart_client.get_cart(), Cart)

    assert response.status_code == 200, "wc-ajax reports errors in the body, not in the status code"
    assert response.json()["error"] is True
    assert cart.items_count == 0


@allure.story("Store API protection")
@allure.title("Store API cart write without nonce is rejected with 401")
@allure.description(
    "WooCommerce Store API protects cart writes with the `X-WC-Store-API-Nonce` header. "
    "This shop never exposes the nonce to guests, so the cart is driven through wc-ajax instead."
)
@allure.link(
    "https://github.com/woocommerce/woocommerce/blob/trunk/plugins/woocommerce/src/StoreApi/docs/nonce-tokens.md",
    name="Store API nonce docs",
)
@allure.severity(allure.severity_level.NORMAL)
@allure.tag("negative", "security")
def test_store_api_write_requires_nonce(cart_client: CartClient) -> None:
    response = cart_client.store_api_add_item(APPLE_WATCH.id)

    assert response.status_code == 401
    assert parse_response(response, ApiError).code == "woocommerce_rest_missing_nonce"
