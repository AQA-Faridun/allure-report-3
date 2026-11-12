from typing import Self

import allure
from playwright.sync_api import Page

from intershop.pages.components.header import HeaderComponent


class BasePage:
    path = "/"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.header = HeaderComponent(page)
        self.alerts = page.locator("#content").get_by_role("alert")

    def open(self) -> Self:
        with allure.step(f"Open page {self.path}"):
            self.page.goto(self.path)
        return self
