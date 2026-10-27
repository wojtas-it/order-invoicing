from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.errors import CarrierUnavailableError, ConflictError, NotFoundError, ValidationError

STATUS_CODE_BY_ERROR: dict[type[Exception], int] = {
    NotFoundError: 404,
    ConflictError: 409,
    ValidationError: 422,
    CarrierUnavailableError: 502,
}

ErrorHandler = Callable[[Request, Exception], Awaitable[JSONResponse]]


def register_error_handlers(app: FastAPI) -> None:
    for error_type, status_code in STATUS_CODE_BY_ERROR.items():
        app.add_exception_handler(error_type, _json_error_handler(status_code))


def _json_error_handler(status_code: int) -> ErrorHandler:
    async def handle(request: Request, error: Exception) -> JSONResponse:
        return JSONResponse(status_code=status_code, content={"detail": str(error)})

    return handle
