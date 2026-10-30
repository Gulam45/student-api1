"""Library member management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Issue, Member
from app.schemas.issues import IssueRead
from app.schemas.members import MemberCreate, MemberRead, MemberUpdate

router = APIRouter(prefix="/members", tags=["members"])


@router.post("", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
def create_member(
    member_data: MemberCreate,
    db: Session = Depends(get_db),
) -> Member:
    """Register a member; email addresses must be unique."""
    member = Member(**member_data.model_dump())
    db.add(member)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A member with this email already exists.",
        ) from error
    db.refresh(member)
    return member


@router.get("", response_model=list[MemberRead])
def list_members(db: Session = Depends(get_db)) -> list[Member]:
    """List all registered members."""
    return list(db.scalars(select(Member).order_by(Member.id)).all())


@router.get("/{member_id}/issues", response_model=list[IssueRead])
def list_member_issues(member_id: int, db: Session = Depends(get_db)) -> list[Issue]:
    """List lending records for one member."""
    if db.get(Member, member_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )
    return list(
        db.scalars(
            select(Issue)
            .where(Issue.member_id == member_id)
            .order_by(Issue.id)
        ).all()
    )


@router.get("/{member_id}", response_model=MemberRead)
def get_member(member_id: int, db: Session = Depends(get_db)) -> Member:
    """Return one member or 404 when the ID is unknown."""
    member = db.get(Member, member_id)
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )
    return member


@router.put("/{member_id}", response_model=MemberRead)
def update_member(
    member_id: int,
    member_data: MemberUpdate,
    db: Session = Depends(get_db),
) -> Member:
    """Replace all editable fields of a member."""
    member = db.get(Member, member_id)
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )
    for field, value in member_data.model_dump().items():
        setattr(member, field, value)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A member with this email already exists.",
        ) from error
    db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, db: Session = Depends(get_db)) -> Response:
    """Delete a member who has no lending history."""
    member = db.get(Member, member_id)
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )
    has_issue_history = db.scalar(
        select(Issue.id).where(Issue.member_id == member_id).limit(1)
    )
    if has_issue_history is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Members with lending history cannot be deleted.",
        )
    db.delete(member)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
