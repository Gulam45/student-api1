"""Business rules for issuing and returning books."""

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Book, Issue, Member
from app.schemas.issues import IssueCreate


class IssueNotFoundError(Exception):
    """Raised when an issue record does not exist."""


class BookNotFoundError(Exception):
    """Raised when the requested book does not exist."""


class MemberNotFoundError(Exception):
    """Raised when the requested member does not exist."""


class BookUnavailableError(Exception):
    """Raised when a book already has an active issue."""


class IssueConflictError(Exception):
    """Raised when an issue cannot be returned in its current state."""


class InvalidIssueDateError(Exception):
    """Raised when a due date precedes the issue date."""


class InvalidReturnDateError(Exception):
    """Raised when a return date precedes the issue date."""


def issue_book(db: Session, request: IssueCreate) -> Issue:
    """Create a two-week loan after validating its book and member."""
    book = db.get(Book, request.book_id)
    if book is None:
        raise BookNotFoundError

    member = db.get(Member, request.member_id)
    if member is None:
        raise MemberNotFoundError

    if not book.available:
        raise BookUnavailableError

    issue_date = date.today()
    due_date = request.due_date or issue_date + timedelta(days=14)
    if due_date < issue_date:
        raise InvalidIssueDateError

    book.available = False
    issue = Issue(
        book_id=book.id,
        member_id=member.id,
        issue_date=issue_date,
        due_date=due_date,
    )
    db.add(issue)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise BookUnavailableError from error
    db.refresh(issue)
    return issue


def return_book(db: Session, issue_id: int, return_date: date | None) -> Issue:
    """Close an active loan and restore the book's availability."""
    issue = db.scalar(select(Issue).where(Issue.id == issue_id))
    if issue is None:
        raise IssueNotFoundError
    if issue.return_date is not None:
        raise IssueConflictError

    actual_return_date = return_date or date.today()
    if actual_return_date < issue.issue_date:
        raise InvalidReturnDateError

    issue.return_date = actual_return_date
    issue.book.available = True
    db.commit()
    db.refresh(issue)
    return issue
