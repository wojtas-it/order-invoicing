import os
from dataclasses import dataclass, field

DEFAULT_DATABASE_URL = "sqlite:///./orders.db"


@dataclass(frozen=True)
class SellerInfo:
    name: str = "Demo Shop Sp. z o.o."
    street: str = "ul. Przykładowa 1"
    city: str = "Tarnów"
    postal_code: str = "33-100"
    tax_id: str = "1234563218"


@dataclass(frozen=True)
class Settings:
    database_url: str = DEFAULT_DATABASE_URL
    carrier_api_url: str | None = None
    carrier_api_key: str = ""
    seller: SellerInfo = field(default_factory=SellerInfo)

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            database_url=os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL),
            carrier_api_url=os.environ.get("CARRIER_API_URL") or None,
            carrier_api_key=os.environ.get("CARRIER_API_KEY", ""),
        )
