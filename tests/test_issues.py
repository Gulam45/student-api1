"""Tests for book issue and return endpoints."""

from datetime import date, timedelta

from fastapi.testclient import TestClient


def test_issue_book_and_list_issues(
    client: TestClient,
    created_book: dict[str, object],
    created_member: dict[str, object],
) -> None:
    response = client.post(
        "/issues",
        json={
            "book_id": created_book["id"],
            "member_id": created_member["id"],
        },
    )

    assert response.status_code == 201
    issue = response.json()
    assert issue["book_id"] == created_book["id"]
    assert issue["book_title"] == created_book["title"]
    assert issue["member_id"] == created_member["id"]
    assert issue["member_name"] == created_member["full_name"]
    assert issue["issue_date"] == date.today().isoformat()
    assert issue["due_date"] == (date.today() + timedelta(days=14)).isoformat()
    assert issue["return_date"] is None
    assert issue["overdue_days"] == 0
    assert client.get("/issues").json() == [issue]
    assert client.get("/issues?active_only=true").json() == [issue]
    assert client.get(f"/members/{created_member['id']}/issues").json() == [issue]
    assert client.get(f"/books/{created_book['id']}").json()["available"] is False


def test_cannot_issue_unavailable_book(
    client: TestClient,
    created_book: dict[str, object],
    created_member: dict[str, object],
) -> None:
    payload = {
        "book_id": created_book["id"],
        "member_id": created_member["id"],
    }
    assert client.post("/issues", json=payload).status_code == 201
    response = client.post("/issues", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "Book is not available for issue."


def test_return_book_calculates_overdue_days(
    client: TestClient,
    created_book: dict[str, object],
    created_member: dict[str, object],
) -> None:
    due_date = date.today() + timedelta(days=1)
    issue = client.post(
        "/issues",
        json={
            "book_id": created_book["id"],
            "member_id": created_member["id"],
            "due_date": due_date.isoformat(),
        },
    ).json()

    return_date = due_date + timedelta(days=3)
    response = client.post(
        f"/issues/{issue['id']}/return",
        json={"return_date": return_date.isoformat()},
    )

    assert response.status_code == 200
    assert response.json()["return_date"] == return_date.isoformat()
    assert response.json()["overdue_days"] == 3
    assert client.get(f"/books/{created_book['id']}").json()["available"] is True
    assert client.get("/issues?active_only=true").json() == []
    assert client.get("/issues").json() == [response.json()]
    assert client.get(f"/members/{created_member['id']}/issues").json() == [
        response.json()
    ]
    reissued = client.post(
        "/issues",
        json={
            "book_id": created_book["id"],
            "member_id": created_member["id"],
        },
    )
    assert reissued.status_code == 201


def test_unknown_issue_and_repeated_return(
    client: TestClient,
    created_book: dict[str, object],
    created_member: dict[str, object],
) -> None:
    assert client.post("/issues/999/return").status_code == 404
    issue = client.post(
        "/issues",
        json={
            "book_id": created_book["id"],
            "member_id": created_member["id"],
        },
    ).json()
    assert client.post(f"/issues/{issue['id']}/return").status_code == 200
    assert client.post(f"/issues/{issue['id']}/return").status_code == 409


def test_issue_validation_and_unknown_book_or_member(
    client: TestClient,
    created_book: dict[str, object],
    created_member: dict[str, object],
) -> None:
    assert client.post("/issues", json={"book_id": 0, "member_id": 1}).status_code == 422
    assert client.post(
        "/issues",
        json={"book_id": 999, "member_id": created_member["id"]},
    ).status_code == 404
    assert client.post(
        "/issues",
        json={"book_id": created_book["id"], "member_id": 999},
    ).status_code == 404
    assert client.post(
        "/issues",
        json={
            "book_id": created_book["id"],
            "member_id": created_member["id"],
            "due_date": (date.today() - timedelta(days=1)).isoformat(),
        },
    ).status_code == 422


def test_return_date_before_issue_date_is_rejected(
    client: TestClient,
    created_book: dict[str, object],
    created_member: dict[str, object],
) -> None:
    issue = client.post(
        "/issues",
        json={
            "book_id": created_book["id"],
            "member_id": created_member["id"],
        },
    ).json()
    response = client.post(
        f"/issues/{issue['id']}/return",
        json={"return_date": (date.today() - timedelta(days=1)).isoformat()},
    )

    assert response.status_code == 422
    assert client.get(f"/books/{created_book['id']}").json()["available"] is False
