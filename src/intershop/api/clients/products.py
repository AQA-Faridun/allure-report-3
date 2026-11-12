from typing import Any

import allure
import httpx

from intershop.api.base_client import BaseApiClient

STORE_API = "/wp-json/wc/store"


class ProductsClient(BaseApiClient):
    """Read-only catalog endpoints of the WooCommerce Store API."""

    @allure.step("API: get product list")
    def list_products(self, **params: Any) -> httpx.Response:
        return self.get(f"{STORE_API}/products", params=params)

    @allure.step("API: get product #{product_id}")
    def get_product(self, product_id: int) -> httpx.Response:
        return self.get(f"{STORE_API}/products/{product_id}")

    @allure.step("API: get product categories")
    def list_categories(self) -> httpx.Response:
        return self.get(f"{STORE_API}/products/categories")

    @allure.step("API: get product category #{category_id}")
    def get_category(self, category_id: int) -> httpx.Response:
        return self.get(f"{STORE_API}/products/categories/{category_id}")

    @allure.step("API: get product reviews")
    def list_reviews(self, **params: Any) -> httpx.Response:
        return self.get(f"{STORE_API}/products/reviews", params=params)

    @allure.step("API: get catalog collection data")
    def get_collection_data(self, **params: Any) -> httpx.Response:
        return self.get(f"{STORE_API}/products/collection-data", params=params)
