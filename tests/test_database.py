"""SQLite persistence tests."""

from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Book


def test_book_data_persists_after_database_reconnect(tmp_path: Path) -> None:
    database_path = tmp_path / "persistent-test.db"
    database_url = f"sqlite:///{database_path.as_posix()}"
    first_engine = create_engine(database_url)
    Base.metadata.create_all(bind=first_engine)
    with Session(first_engine) as session:
        session.add(
            Book(title="Persistent", author="Test Author", category="Testing")
        )
        session.commit()
    first_engine.dispose()

    second_engine = create_engine(database_url)
    try:
        with Session(second_engine) as session:
            book = session.scalar(select(Book).where(Book.title == "Persistent"))
            assert book is not None
            assert book.author == "Test Author"
    finally:
        second_engine.dispose()
