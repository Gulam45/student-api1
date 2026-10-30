"""Application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.books import router as books_router
from app.api.issues import router as issues_router
from app.api.members import router as members_router
from app.database import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Create missing database tables when the application starts."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Library Management API",
    description="Manage books, members, and book loans.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(books_router)
app.include_router(members_router)
app.include_router(issues_router)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Direct browser visits to the interactive API documentation."""
    return RedirectResponse(url="/docs")
