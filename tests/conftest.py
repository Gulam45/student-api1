"""Shared fixtures for API tests."""

from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Book, Issue, Member


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Run each API test against a fresh in-memory SQLite database."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(test_engine, "connect")
    def enable_foreign_keys(connection: Any, _: Any) -> None:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=test_engine)

    def override_get_db() -> Generator[Session, None, None]:
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


@pytest.fixture
def book_payload() -> dict[str, str]:
    return {
        "title": "The Hobbit",
        "author": "J. R. R. Tolkien",
        "category": "Fantasy",
    }


@pytest.fixture
def member_payload() -> dict[str, str]:
    return {
        "full_name": "Asha Rao",
        "email": "asha@example.com",
        "phone": "555-0100",
    }


@pytest.fixture
def created_book(client: TestClient, book_payload: dict[str, str]) -> dict[str, object]:
    response = client.post("/books", json=book_payload)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def created_member(
    client: TestClient,
    member_payload: dict[str, str],
) -> dict[str, object]:
    response = client.post("/members", json=member_payload)
    assert response.status_code == 201
    return response.json()
