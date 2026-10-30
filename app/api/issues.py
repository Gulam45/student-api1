"""Book issue and return endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Issue
from app.schemas.issues import IssueCreate, IssueRead, ReturnRequest
from app.services.issues import (
    BookNotFoundError,
    BookUnavailableError,
    InvalidIssueDateError,
    IssueConflictError,
    IssueNotFoundError,
    InvalidReturnDateError,
    MemberNotFoundError,
    issue_book,
    return_book,
)

router = APIRouter(prefix="/issues", tags=["issues"])


@router.post("", response_model=IssueRead, status_code=status.HTTP_201_CREATED)
def create_issue(
    issue_data: IssueCreate,
    db: Session = Depends(get_db),
) -> Issue:
    """Issue an available book to an existing member."""
    try:
        return issue_book(db, issue_data)
    except BookNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        ) from error
    except MemberNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        ) from error
    except BookUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book is not available for issue.",
        ) from error
    except InvalidIssueDateError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Due date cannot be before the issue date.",
        ) from error


@router.get("", response_model=list[IssueRead])
def list_issues(
    active_only: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> list[Issue]:
    """List all lending records or only active loans."""
    statement = select(Issue).order_by(Issue.id)
    if active_only:
        statement = statement.where(Issue.return_date.is_(None))
    return list(db.scalars(statement).all())


@router.post("/{issue_id}/return", response_model=IssueRead)
def return_issue(
    issue_id: int,
    request: ReturnRequest | None = None,
    db: Session = Depends(get_db),
) -> Issue:
    """Return an issued book and calculate overdue days."""
    try:
        return return_book(
            db,
            issue_id,
            request.return_date if request is not None else None,
        )
    except IssueNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        ) from error
    except IssueConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This book has already been returned.",
        ) from error
    except InvalidReturnDateError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Return date cannot be before the issue date.",
        ) from error
