import time
from typing import Any

import allure
import httpx

from intershop.utils.attachments import attach_http_exchange


class BaseApiClient:
    """Thin httpx wrapper: every request becomes an Allure step with the HTTP exchange attached.

    Clients share one httpx.Client, so cookies (WooCommerce session, login) are shared too.
    """

    def __init__(self, http: httpx.Client) -> None:
        self._http = http

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        with allure.step(f"{method} {url}"):
            started_at_ms = int(time.time() * 1000)
            response = self._http.request(method, url, **kwargs)
            attach_http_exchange(response, started_at_ms)
            return response

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("POST", url, **kwargs)


def create_http_client(base_url: str, timeout_s: float) -> httpx.Client:
    return httpx.Client(
        base_url=base_url,
        timeout=timeout_s,
        follow_redirects=True,
        headers={"User-Agent": "intershop-allure3-demo/0.1 (+httpx)"},
    )
