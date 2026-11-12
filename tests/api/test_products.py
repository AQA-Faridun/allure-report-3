import math

import allure
import pytest

from intershop.api.clients.products import ProductsClient
from intershop.api.schema import parse_response
from intershop.data.catalog import APPLE_WATCH, IPAD_2020, NON_EXISTENT_ID, PHONES_CATEGORY_ID
from intershop.models.store import ApiError, CollectionData, Product

pytestmark = [pytest.mark.api, pytest.mark.regression]


@allure.epic("Catalog")
@allure.feature("Products API")
@allure.label("owner", "catalog-team")
@allure.suite("Store API: products")
class TestProductList:
    @pytest.mark.smoke
    @allure.story("Product list")
    @allure.title("Product list returns 200 and every item matches the Product schema")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("smoke", "schema")
    @allure.testcase("CAT-101")
    def test_product_list_matches_schema(self, products_client: ProductsClient) -> None:
        response = products_client.list_products()

        assert response.status_code == 200
        products = parse_response(response, list[Product])
        assert products, "Catalog must not be empty"

    @allure.story("Pagination")
    @allure.title("Product list returns exactly {per_page} item(s) per page")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("per_page", [1, 5, 10])
    def test_product_list_respects_per_page(self, products_client: ProductsClient, per_page: int) -> None:
        response = products_client.list_products(per_page=per_page)

        assert response.status_code == 200
        assert len(parse_response(response, list[Product])) == per_page

    @allure.story("Pagination")
    @allure.title("X-WP-TotalPages header is consistent with X-WP-Total and per_page")
    @allure.severity(allure.severity_level.MINOR)
    def test_pagination_headers_are_consistent(self, products_client: ProductsClient) -> None:
        per_page = 7

        response = products_client.list_products(per_page=per_page)

        assert response.status_code == 200
        total = int(response.headers["X-WP-Total"])
        assert int(response.headers["X-WP-TotalPages"]) == math.ceil(total / per_page)

    @allure.story("Pagination")
    @allure.title("per_page={per_page} is rejected with 400 rest_invalid_param")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negative")
    @pytest.mark.parametrize("per_page", [101, -1, "abc"])
    def test_invalid_per_page_is_rejected(self, products_client: ProductsClient, per_page: object) -> None:
        response = products_client.list_products(per_page=per_page)

        assert response.status_code == 400
        assert parse_response(response, ApiError).code == "rest_invalid_param"


@allure.epic("Catalog")
@allure.feature("Products API")
@allure.label("owner", "catalog-team")
@allure.suite("Store API: products")
class TestSingleProduct:
    @allure.story("Product details")
    @allure.title("Product details match the same product in the list")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.testcase("CAT-102")
    def test_product_details_match_list_item(self, products_client: ProductsClient) -> None:
        listed = parse_response(products_client.list_products(search=APPLE_WATCH.name), list[Product])[0]

        response = products_client.get_product(listed.id)

        assert response.status_code == 200
        details = parse_response(response, Product)
        assert details == listed

    @allure.story("Product details")
    @allure.title("Unknown product id returns 404 woocommerce_rest_product_invalid_id")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negative")
    def test_unknown_product_returns_404(self, products_client: ProductsClient) -> None:
        response = products_client.get_product(NON_EXISTENT_ID)

        assert response.status_code == 404
        error = parse_response(response, ApiError)
        assert error.code == "woocommerce_rest_product_invalid_id"
        assert error.data.status == 404


@allure.epic("Catalog")
@allure.feature("Search and filters API")
@allure.label("owner", "catalog-team")
@allure.suite("Store API: search and filters")
class TestSearchAndFilters:
    @allure.story("Search")
    @allure.title("Search '{query}' finds '{expected_name}'")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        ("query", "expected_name"),
        [("apple", APPLE_WATCH.name), ("ipad", IPAD_2020.name)],
        ids=["apple", "ipad"],
    )
    def test_search_finds_product(
        self, products_client: ProductsClient, query: str, expected_name: str
    ) -> None:
        response = products_client.list_products(search=query)

        assert response.status_code == 200
        names = [product.name for product in parse_response(response, list[Product])]
        assert expected_name in names

    @allure.story("Search")
    @allure.title("Search without matches returns an empty list")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("negative")
    def test_search_without_matches_returns_empty_list(self, products_client: ProductsClient) -> None:
        response = products_client.list_products(search="zzz-no-such-product-zzz")

        assert response.status_code == 200
        assert response.json() == []

    @allure.story("Sorting")
    @allure.title("Products are sorted by price, order={order}")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("order", ["asc", "desc"])
    def test_products_are_sorted_by_price(self, products_client: ProductsClient, order: str) -> None:
        response = products_client.list_products(orderby="price", order=order, per_page=20)

        assert response.status_code == 200
        prices = [product.prices.price_value for product in parse_response(response, list[Product])]
        assert prices == sorted(prices, reverse=order == "desc")

    @allure.story("Filters")
    @allure.title("on_sale filter returns only discounted products")
    @allure.severity(allure.severity_level.NORMAL)
    def test_on_sale_filter_returns_discounted_products(self, products_client: ProductsClient) -> None:
        response = products_client.list_products(on_sale="true", per_page=50)

        assert response.status_code == 200
        products = parse_response(response, list[Product])
        assert products
        for product in products:
            with allure.step(f"Check discount of '{product.name}'"):
                assert product.on_sale
                assert product.prices.price_value < product.prices.regular_price_value

    @allure.story("Filters")
    @allure.title("Category filter returns only products of that category")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_category_filter_returns_category_products(self, products_client: ProductsClient) -> None:
        response = products_client.list_products(category=PHONES_CATEGORY_ID, per_page=50)

        assert response.status_code == 200
        products = parse_response(response, list[Product])
        assert products
        assert all(PHONES_CATEGORY_ID in {c.id for c in product.categories} for product in products)

    @allure.story("Filters")
    @allure.title("Catalog price range starts at the cheapest product price")
    @allure.severity(allure.severity_level.MINOR)
    def test_price_range_matches_cheapest_product(self, products_client: ProductsClient) -> None:
        cheapest = parse_response(
            products_client.list_products(orderby="price", order="asc", per_page=1), list[Product]
        )[0]

        response = products_client.get_collection_data(calculate_price_range="true")

        assert response.status_code == 200
        price_range = parse_response(response, CollectionData).price_range
        min_price = price_range.to_decimal(price_range.min_price)
        assert min_price <= price_range.to_decimal(price_range.max_price)
        assert min_price == cheapest.prices.price_value
