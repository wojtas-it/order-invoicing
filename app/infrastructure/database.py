from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.orm import Base

IN_MEMORY_SQLITE_URLS = ("sqlite://", "sqlite:///:memory:")


def create_session_factory(database_url: str) -> sessionmaker[Session]:
    engine = _create_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


def _create_engine(database_url: str) -> Engine:
    if not database_url.startswith("sqlite"):
        return create_engine(database_url)
    connect_args = {"check_same_thread": False}
    if database_url in IN_MEMORY_SQLITE_URLS:
        # A single shared connection keeps the in-memory database alive between sessions.
        return create_engine(database_url, connect_args=connect_args, poolclass=StaticPool)
    return create_engine(database_url, connect_args=connect_args)
