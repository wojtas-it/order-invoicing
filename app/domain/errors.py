class DomainError(Exception):
    """Base class for all business rule violations."""


class ValidationError(DomainError):
    pass


class UnknownDiscountCodeError(ValidationError):
    def __init__(self, code: str) -> None:
        super().__init__(f"Nieznany kod rabatowy: {code}")


class NotFoundError(DomainError):
    pass


class OrderNotFoundError(NotFoundError):
    def __init__(self, order_id: int) -> None:
        super().__init__(f"Nie znaleziono zamówienia o id {order_id}")


class InvoiceNotFoundError(NotFoundError):
    def __init__(self, invoice_id: int) -> None:
        super().__init__(f"Nie znaleziono faktury o id {invoice_id}")


class ConflictError(DomainError):
    pass


class InvalidStatusTransitionError(ConflictError):
    def __init__(self, current: str, target: str) -> None:
        super().__init__(f"Nie można zmienić statusu zamówienia z „{current}” na „{target}”")


class InvoiceNotAllowedError(ConflictError):
    def __init__(self, order_id: int) -> None:
        super().__init__(f"Zamówienie {order_id} musi być opłacone, aby wystawić fakturę")


class InvoiceAlreadyIssuedError(ConflictError):
    def __init__(self, order_id: int) -> None:
        super().__init__(f"Faktura dla zamówienia {order_id} została już wystawiona")


class CarrierUnavailableError(DomainError):
    pass
