"""Test data factories built on mimesis."""

import string
from dataclasses import dataclass

from mimesis import Address, Locale, Person
from mimesis.random import Random

# The site rejects registration fields longer than 20 characters ("Максимальное допустимое
# количество символов: 20"), so usernames and emails are kept short on purpose.
MAX_FIELD_LENGTH = 20
EMAIL_DOMAIN = "ex.io"


@dataclass(frozen=True)
class Customer:
    username: str
    email: str
    password: str


@dataclass(frozen=True)
class BillingAddress:
    first_name: str
    last_name: str
    street: str
    city: str
    region: str
    postcode: str
    phone: str


class CustomerFactory:
    def __init__(self, seed: int | None = None) -> None:
        self._random = Random(seed)
        self._person = Person(Locale.EN, seed=seed)

    def build(self) -> Customer:
        username = "qa" + "".join(self._random.choices(string.ascii_lowercase + string.digits, k=8))
        return Customer(
            username=username,
            email=f"{username}@{EMAIL_DOMAIN}",
            password=self._person.password(length=12) + "A1!",
        )


class BillingAddressFactory:
    def __init__(self, seed: int | None = None) -> None:
        self._person = Person(Locale.RU, seed=seed)
        self._address = Address(Locale.RU, seed=seed)

    def build(self) -> BillingAddress:
        return BillingAddress(
            first_name=self._person.first_name(),
            last_name=self._person.last_name(),
            street=self._address.address(),
            city=self._address.city(),
            region=self._address.region(),
            postcode=self._address.postal_code(),
            phone=self._person.phone_number(mask="+7##########"),
        )
