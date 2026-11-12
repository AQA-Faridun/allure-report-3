"""Stable reference data of the live catalog (checked against /wp-json/wc/store on 2026-10-20)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class KnownProduct:
    id: int
    name: str
    slug: str
    category_slug: str


APPLE_WATCH = KnownProduct(id=15, name="Apple Watch 6", slug="apple-watch", category_slug="watch")
IPAD_2020 = KnownProduct(id=53, name="iPad 2020 32gb wi-fi", slug="ipad-2020-32gb-wi-fi", category_slug="pad")

PHONES_CATEGORY_ID = 24
STORE_PAGE_SIZE = 12
STORE_API_MAX_PER_PAGE = 100
NON_EXISTENT_ID = 99_999_999
