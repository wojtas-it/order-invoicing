import re
from dataclasses import dataclass

from app.domain.errors import ValidationError
from app.domain.tax_id import is_valid_nip, normalize_nip

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
POSTAL_CODE_PATTERN = re.compile(r"^\d{2}-\d{3}$")
REQUIRED_TEXT_FIELDS = {"name": "Nazwa klienta", "street": "Ulica", "city": "Miasto"}


@dataclass(frozen=True)
class Customer:
    name: str
    email: str
    street: str
    city: str
    postal_code: str
    tax_id: str | None = None

    def __post_init__(self) -> None:
        for field_name, label in REQUIRED_TEXT_FIELDS.items():
            if not getattr(self, field_name).strip():
                raise ValidationError(f"{label} nie może być puste")
        if not EMAIL_PATTERN.match(self.email):
            raise ValidationError(f"Niepoprawny adres e-mail: {self.email}")
        if not POSTAL_CODE_PATTERN.match(self.postal_code):
            raise ValidationError(f"Kod pocztowy musi mieć format XX-XXX: {self.postal_code}")
        if self.tax_id is not None:
            if not is_valid_nip(self.tax_id):
                raise ValidationError(f"Niepoprawny NIP: {self.tax_id}")
            object.__setattr__(self, "tax_id", normalize_nip(self.tax_id))

    @property
    def is_company(self) -> bool:
        return self.tax_id is not None
