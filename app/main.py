from fastapi import FastAPI

from app.api import invoices, orders
from app.api.errors import register_error_handlers
from app.config import Settings
from app.infrastructure.carrier import build_carrier_client
from app.infrastructure.clock import SystemClock
from app.infrastructure.database import create_session_factory
from app.services.ports import CarrierClient, Clock


def create_app(
    settings: Settings | None = None,
    carrier: CarrierClient | None = None,
    clock: Clock | None = None,
) -> FastAPI:
    settings = settings or Settings.from_env()
    app = FastAPI(
        title="Order Invoicing",
        version="0.1.0",
        description="Obsługa zamówień z fakturowaniem i integracją z przewoźnikiem.",
    )
    app.state.settings = settings
    app.state.session_factory = create_session_factory(settings.database_url)
    app.state.carrier = carrier or build_carrier_client(settings)
    app.state.clock = clock or SystemClock()

    app.include_router(orders.router)
    app.include_router(invoices.router)
    register_error_handlers(app)

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
