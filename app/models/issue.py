"""Book issue and return database model."""

from datetime import date

from sqlalchemy import Date, ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Issue(Base):
    """A lending record, including return and overdue information."""

    __tablename__ = "issues"
    __table_args__ = (
        Index(
            "uq_issues_active_book",
            "book_id",
            unique=True,
            sqlite_where=text("return_date IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    member_id: Mapped[int] = mapped_column(
        ForeignKey("members.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    book: Mapped["Book"] = relationship(back_populates="issues")
    member: Mapped["Member"] = relationship(back_populates="issues")

    @property
    def overdue_days(self) -> int:
        """Return the number of late days, or zero for an active/on-time loan."""
        if self.return_date is None:
            return 0
        return max((self.return_date - self.due_date).days, 0)

    @property
    def book_title(self) -> str:
        """Expose the related book title in issue responses."""
        return self.book.title

    @property
    def member_name(self) -> str:
        """Expose the related member name in issue responses."""
        return self.member.full_name
