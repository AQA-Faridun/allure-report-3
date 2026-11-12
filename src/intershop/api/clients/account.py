import re

import allure
import httpx

from intershop.api.base_client import BaseApiClient
from intershop.data.factories import Customer


class AccountClient(BaseApiClient):
    """Account forms of the shop (there is no public REST API for them).

    Each form carries a WooCommerce nonce, so the page is fetched first and the nonce is reused.
    """

    def register(self, customer: Customer) -> httpx.Response:
        with allure.step(f"API: register customer '{customer.username}'"):
            return self._submit_registration(customer)

    def _submit_registration(self, customer: Customer) -> httpx.Response:
        nonce = self._form_nonce("/register/", "woocommerce-register-nonce")
        return self.post(
            "/register/",
            data={
                "username": customer.username,
                "email": customer.email,
                "password": customer.password,
                "woocommerce-register-nonce": nonce,
                "_wp_http_referer": "/register/",
                "register": "Зарегистрироваться",
            },
        )

    @allure.step("API: log in as {username}")
    def login(self, username: str, password: str) -> httpx.Response:
        nonce = self._form_nonce("/my-account/", "woocommerce-login-nonce")
        return self.post(
            "/my-account/",
            data={
                "username": username,
                "password": password,
                "woocommerce-login-nonce": nonce,
                "_wp_http_referer": "/my-account/",
                "login": "Войти",
            },
        )

    @allure.step("API: open account page")
    def open_account_page(self) -> httpx.Response:
        return self.get("/my-account/")

    @staticmethod
    def error_text(html: str) -> str:
        """Plain text of the WooCommerce error notice on a page, or '' if there is none."""
        match = re.search(r'<ul class="woocommerce-error"[^>]*>(.*?)</ul>', html, re.DOTALL)
        if match is None:
            return ""
        return " ".join(re.sub(r"<[^>]+>", " ", match.group(1)).split())

    def _form_nonce(self, page_path: str, field_name: str) -> str:
        html = self.get(page_path).raise_for_status().text
        match = re.search(rf'name="{re.escape(field_name)}" value="([0-9a-f]+)"', html)
        if match is None:
            raise AssertionError(f"Nonce '{field_name}' not found on {page_path}")
        return match.group(1)
