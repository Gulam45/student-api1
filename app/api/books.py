"""Book management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book, Issue
from app.schemas.books import BookCreate, BookRead, BookUpdate

router = APIRouter(prefix="/books", tags=["books"])


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(book_data: BookCreate, db: Session = Depends(get_db)) -> Book:
    """Add a book to the catalog."""
    book = Book(**book_data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.get("", response_model=list[BookRead])
def list_books(db: Session = Depends(get_db)) -> list[Book]:
    """List all books in catalog order."""
    return list(db.scalars(select(Book).order_by(Book.id)).all())


@router.get("/search", response_model=list[BookRead])
def search_books(
    title: str | None = Query(default=None, min_length=1),
    author: str | None = Query(default=None, min_length=1),
    category: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
) -> list[Book]:
    """Search case-insensitively by one or more book fields."""
    filters = []
    if title is not None:
        filters.append(Book.title.ilike(f"%{title.strip()}%"))
    if author is not None:
        filters.append(Book.author.ilike(f"%{author.strip()}%"))
    if category is not None:
        filters.append(Book.category.ilike(f"%{category.strip()}%"))
    search_values = (title, author, category)
    if not filters or any(
        not value.strip() for value in search_values if value is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide at least one non-empty title, author, or category.",
        )
    return list(
        db.scalars(select(Book).where(*filters).order_by(Book.id)).all()
    )


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)) -> Book:
    """Return one book or 404 when it does not exist."""
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.put("/{book_id}", response_model=BookRead)
def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
) -> Book:
    """Replace all editable fields of a book."""
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    for field, value in book_data.model_dump().items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)) -> Response:
    """Delete a book that has no lending history."""
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    has_issue_history = db.scalar(
        select(Issue.id).where(Issue.book_id == book_id).limit(1)
    )
    if has_issue_history is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Books with lending history cannot be deleted.",
        )
    db.delete(book)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
