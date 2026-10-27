from uuid import uuid4

import httpx

from app.config import Settings
from app.domain.errors import CarrierUnavailableError
from app.services.ports import CarrierClient, ShipmentRequest

DEFAULT_TIMEOUT_SECONDS = 5.0


class HttpCarrierClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._http = http_client or httpx.Client(timeout=DEFAULT_TIMEOUT_SECONDS)

    def create_shipment(self, request: ShipmentRequest) -> str:
        try:
            response = self._http.post(
                f"{self._base_url}/shipments",
                json=_shipment_payload(request),
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            response.raise_for_status()
            tracking_number = response.json().get("tracking_number")
        except (httpx.HTTPError, ValueError) as error:
            raise CarrierUnavailableError(f"Błąd komunikacji z przewoźnikiem: {error}") from error
        if not tracking_number:
            raise CarrierUnavailableError("Przewoźnik nie zwrócił numeru przesyłki")
        return tracking_number


class FakeCarrierClient:
    """Offline carrier used when no carrier API is configured."""

    def create_shipment(self, request: ShipmentRequest) -> str:
        return f"FAKE{uuid4().hex[:12].upper()}"


def build_carrier_client(settings: Settings) -> CarrierClient:
    if settings.carrier_api_url:
        return HttpCarrierClient(settings.carrier_api_url, settings.carrier_api_key)
    return FakeCarrierClient()


def _shipment_payload(request: ShipmentRequest) -> dict[str, str | int]:
    return {
        "reference": request.order_id,
        "service": request.shipping_method.value,
        "receiver": {
            "name": request.recipient_name,
            "email": request.recipient_email,
            "street": request.street,
            "city": request.city,
            "postal_code": request.postal_code,
        },
    }
