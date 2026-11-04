"""Error responses shown in the OpenAPI (Swagger) documentation."""

from typing import Any

from app.api.schemas import ErrorResponse

ResponsesDoc = dict[int | str, dict[str, Any]]

NOT_FOUND: ResponsesDoc = {404: {"model": ErrorResponse, "description": "Nie znaleziono"}}
INVALID_DATA: ResponsesDoc = {422: {"model": ErrorResponse, "description": "Niepoprawne dane"}}
STATUS_CONFLICT: ResponsesDoc = {
    **NOT_FOUND,
    409: {"model": ErrorResponse, "description": "Niedozwolona zmiana statusu"},
}
CARRIER_UNAVAILABLE: ResponsesDoc = {
    502: {"model": ErrorResponse, "description": "Przewoźnik niedostępny"},
}
