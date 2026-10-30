"""Book request and response schemas."""

from pydantic import BaseModel, ConfigDict, Field


class BookFields(BaseModel):
    """Validated fields shared by book create and update requests."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=150)
    category: str = Field(min_length=1, max_length=100)


class BookCreate(BookFields):
    """Fields required to add a book."""


class BookUpdate(BookFields):
    """Complete set of editable book fields."""


class BookRead(BookFields):
    """Book representation returned by the API."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    id: int
    available: bool
