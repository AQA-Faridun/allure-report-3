import re
from decimal import Decimal


def parse_rub(text: str) -> Decimal:
    """Turn a shop price like '34990,00₽' or '1 299,50 ₽' into Decimal('34990.00')."""
    digits = re.sub(r"[^\d,]", "", text).replace(",", ".")
    if not digits:
        raise ValueError(f"No price found in {text!r}")
    return Decimal(digits)
