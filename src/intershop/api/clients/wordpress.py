import allure
import httpx

from intershop.api.base_client import BaseApiClient


class WordPressClient(BaseApiClient):
    """Core WP REST API and the protected WooCommerce REST API v3."""

    @allure.step("API: site search for {query}")
    def search(self, query: str) -> httpx.Response:
        return self.get("/wp-json/wp/v2/search", params={"search": query})

    @allure.step("API: get REST API index")
    def get_index(self) -> httpx.Response:
        return self.get("/wp-json/")

    @allure.step("API: list users")
    def list_users(self) -> httpx.Response:
        return self.get("/wp-json/wp/v2/users")

    @allure.step("API: get products from WooCommerce REST API v3 (needs auth)")
    def list_wc_v3_products(self) -> httpx.Response:
        return self.get("/wp-json/wc/v3/products")
