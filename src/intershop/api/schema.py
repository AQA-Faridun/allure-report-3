import allure
import httpx
from pydantic import TypeAdapter


def parse_response[T](response: httpx.Response, model: type[T]) -> T:
    """Validate the JSON body against a pydantic model (or a typing form like list[Model])."""
    with allure.step(f"Validate response body against schema {getattr(model, '__name__', model)}"):
        result: T = TypeAdapter(model).validate_python(response.json())
        return result
