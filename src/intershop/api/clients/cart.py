import allure
import httpx

from intershop.api.base_client import BaseApiClient
from intershop.api.clients.products import STORE_API


class CartClient(BaseApiClient):
    """Guest cart bound to the WooCommerce session cookie of the shared httpx client.

    The Store API cart is read-only for us: write endpoints need a nonce the site never
    exposes, so items are added and removed through the classic wc-ajax endpoints.
    """

    @allure.step("API: get current cart")
    def get_cart(self) -> httpx.Response:
        return self.get(f"{STORE_API}/cart")

    @allure.step("API: add product #{product_id} x{quantity} to cart")
    def add_item(self, product_id: int, quantity: int = 1) -> httpx.Response:
        return self.post(
            "/", params={"wc-ajax": "add_to_cart"}, data={"product_id": product_id, "quantity": quantity}
        )

    @allure.step("API: remove cart item {item_key}")
    def remove_item(self, item_key: str) -> httpx.Response:
        return self.post("/", params={"wc-ajax": "remove_from_cart"}, data={"cart_item_key": item_key})

    @allure.step("API: add product #{product_id} via Store API (no nonce)")
    def store_api_add_item(self, product_id: int, quantity: int = 1) -> httpx.Response:
        return self.post(f"{STORE_API}/cart/add-item", json={"id": product_id, "quantity": quantity})
