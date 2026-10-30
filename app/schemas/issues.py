"""Issue and return request and response schemas."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class IssueCreate(BaseModel):
    """Fields needed to issue a book."""

    book_id: int = Field(gt=0)
    member_id: int = Field(gt=0)
    due_date: date | None = None


class ReturnRequest(BaseModel):
    """Optional return date; omitted values use today's date."""

    return_date: date | None = None


class IssueRead(BaseModel):
    """Lending record returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    book_title: str
    member_id: int
    member_name: str
    issue_date: date
    due_date: date
    return_date: date | None
    overdue_days: int
