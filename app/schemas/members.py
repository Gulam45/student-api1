"""Member request and response schemas."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class MemberFields(BaseModel):
    """Validated fields shared by member create and update requests."""

    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)


class MemberCreate(MemberFields):
    """Fields required to register a member."""


class MemberUpdate(MemberFields):
    """Complete set of editable member fields."""


class MemberRead(MemberFields):
    """Member representation returned by the API."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    id: int
