import allure
import httpx

from intershop.api.base_client import BaseApiClient


class SiteClient(BaseApiClient):
    """Plain HTTP access to storefront HTML pages, without a browser."""

    @allure.step("HTTP: open page {path}")
    def open_page(self, path: str) -> httpx.Response:
        return self.get(path)
