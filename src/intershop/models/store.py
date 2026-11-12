"""Response models for the WooCommerce Store API (/wp-json/wc/store/*) and WP REST API."""

from decimal import Decimal

from pydantic import BaseModel, Field, HttpUrl


class Money(BaseModel):
    currency_code: str
    currency_minor_unit: int = Field(ge=0)

    def to_decimal(self, minor_units: str) -> Decimal:
        return Decimal(minor_units) / Decimal(10) ** self.currency_minor_unit


class ProductPrices(Money):
    price: str
    regular_price: str
    sale_price: str

    @property
    def price_value(self) -> Decimal:
        return self.to_decimal(self.price)

    @property
    def regular_price_value(self) -> Decimal:
        return self.to_decimal(self.regular_price)


class ProductImage(BaseModel):
    id: int
    src: HttpUrl
    thumbnail: HttpUrl


class CategoryRef(BaseModel):
    id: int
    name: str
    slug: str


class Product(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=1)
    type: str
    permalink: HttpUrl
    description: str
    on_sale: bool
    prices: ProductPrices
    images: list[ProductImage]
    categories: list[CategoryRef]
    is_purchasable: bool
    is_in_stock: bool


class Category(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    parent: int = Field(ge=0)
    count: int = Field(ge=0)
    permalink: HttpUrl


class Review(BaseModel):
    id: int
    product_id: int
    product_name: str
    reviewer: str
    review: str
    rating: int = Field(ge=0, le=5)
    verified: bool


class PriceRange(Money):
    min_price: str
    max_price: str


class CollectionData(BaseModel):
    price_range: PriceRange


class CartItemTotals(Money):
    line_subtotal: str
    line_total: str


class CartItem(BaseModel):
    key: str = Field(min_length=32, max_length=32)
    id: int
    quantity: int = Field(gt=0)
    name: str
    prices: ProductPrices
    totals: CartItemTotals


class CartTotals(Money):
    total_items: str
    total_price: str


class Cart(BaseModel):
    items: list[CartItem]
    items_count: int = Field(ge=0)
    needs_payment: bool
    totals: CartTotals


class ApiErrorData(BaseModel):
    status: int


class ApiError(BaseModel):
    code: str
    message: str
    data: ApiErrorData


class SearchResult(BaseModel):
    id: int
    title: str
    url: HttpUrl
    type: str
    subtype: str
