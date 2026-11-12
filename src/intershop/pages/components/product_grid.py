from decimal import Decimal

import allure
from playwright.sync_api import Locator, Page

from intershop.utils.money import parse_rub


class ProductGridComponent:
    """Product tiles on shop, category and search result pages."""

    def __init__(self, page: Page) -> None:
        self.tiles = page.locator("#content ul.products > li")

    def tile(self, product_name: str) -> Locator:
        return self.tiles.filter(has=self.tiles.page.get_by_role("heading", name=product_name, exact=True))

    @allure.step("Read product titles from the grid")
    def titles(self) -> list[str]:
        self.tiles.first.wait_for()
        return [title.strip() for title in self.tiles.get_by_role("heading", level=3).all_inner_texts()]

    @allure.step("Read current product prices from the grid")
    def prices(self) -> list[Decimal]:
        self.tiles.first.wait_for()
        # On sale tiles show the old price in <del> and the current one in <ins>.
        price_boxes = self.tiles.locator(".price")
        return [
            parse_rub(box.locator("ins").inner_text() if box.locator("ins").count() else box.inner_text())
            for box in price_boxes.all()
        ]

    @allure.step("Open product {product_name} from the grid")
    def open_product(self, product_name: str) -> None:
        self.tile(product_name).get_by_role("link", name=product_name, exact=True).click()

    @allure.step("Add {product_name} to cart from the grid")
    def add_to_cart(self, product_name: str) -> None:
        self.tile(product_name).get_by_role("link", name=f"Add “{product_name}” to your cart").click()
