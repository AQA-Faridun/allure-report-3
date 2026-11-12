import allure
import pytest

from intershop.api.clients.products import ProductsClient
from intershop.api.schema import parse_response
from intershop.data.catalog import NON_EXISTENT_ID, PHONES_CATEGORY_ID
from intershop.models.store import ApiError, Category, Review

pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    allure.epic("Catalog"),
    allure.label("owner", "catalog-team"),
    allure.suite("Store API: categories and reviews"),
]


@allure.feature("Categories API")
class TestCategories:
    @pytest.mark.smoke
    @allure.story("Category list")
    @allure.title("Category list matches the Category schema")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "schema")
    def test_category_list_matches_schema(self, products_client: ProductsClient) -> None:
        response = products_client.list_categories()

        assert response.status_code == 200
        assert parse_response(response, list[Category])

    @allure.story("Category tree")
    @allure.title("Category '{slug}' exists and its parent is in the tree")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("slug", ["phones", "pad", "tv", "watch"])
    def test_category_parent_exists(self, products_client: ProductsClient, slug: str) -> None:
        categories = parse_response(products_client.list_categories(), list[Category])
        by_slug = {category.slug: category for category in categories}
        ids = {category.id for category in categories}

        assert slug in by_slug, f"Category '{slug}' is missing"
        assert by_slug[slug].parent in ids

    @allure.story("Category details")
    @allure.title("Category details are returned by id")
    @allure.severity(allure.severity_level.NORMAL)
    def test_category_by_id(self, products_client: ProductsClient) -> None:
        response = products_client.get_category(PHONES_CATEGORY_ID)

        assert response.status_code == 200
        category = parse_response(response, Category)
        assert category.id == PHONES_CATEGORY_ID
        assert category.slug == "phones"

    @allure.story("Category details")
    @allure.title("Unknown category id returns 404")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("negative")
    def test_unknown_category_returns_404(self, products_client: ProductsClient) -> None:
        response = products_client.get_category(NON_EXISTENT_ID)

        assert response.status_code == 404
        assert parse_response(response, ApiError).code == "woocommerce_rest_category_invalid_id"


@allure.feature("Reviews API")
class TestReviews:
    @allure.story("Review list")
    @allure.title("Review list matches the Review schema")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("schema")
    def test_review_list_matches_schema(self, products_client: ProductsClient) -> None:
        response = products_client.list_reviews()

        assert response.status_code == 200
        assert parse_response(response, list[Review])

    @allure.story("Review list")
    @allure.title("Reviews can be filtered by product")
    @allure.severity(allure.severity_level.TRIVIAL)
    def test_reviews_filtered_by_product(self, products_client: ProductsClient) -> None:
        reviewed_product_id = parse_response(products_client.list_reviews(), list[Review])[0].product_id

        response = products_client.list_reviews(product_id=reviewed_product_id)

        assert response.status_code == 200
        reviews = parse_response(response, list[Review])
        assert {review.product_id for review in reviews} == {reviewed_product_id}
