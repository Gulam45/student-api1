"""Tests for book management endpoints."""

from fastapi.testclient import TestClient


def test_create_and_list_books(
    client: TestClient,
    book_payload: dict[str, str],
) -> None:
    created = client.post("/books", json=book_payload)

    assert created.status_code == 201
    assert created.json() == {
        "id": 1,
        **book_payload,
        "available": True,
    }
    assert client.get("/books").json() == [created.json()]


def test_get_book_by_id(
    client: TestClient,
    created_book: dict[str, object],
) -> None:
    response = client.get(f"/books/{created_book['id']}")

    assert response.status_code == 200
    assert response.json() == created_book


def test_update_and_delete_book(
    client: TestClient,
    created_book: dict[str, object],
) -> None:
    updated = {
        "title": "The Hobbit: Updated",
        "author": "J. R. R. Tolkien",
        "category": "Adventure",
    }
    update_response = client.put(f"/books/{created_book['id']}", json=updated)

    assert update_response.status_code == 200
    assert update_response.json() == {
        "id": created_book["id"],
        **updated,
        "available": True,
    }
    delete_response = client.delete(f"/books/{created_book['id']}")
    assert delete_response.status_code == 204
    assert client.get(f"/books/{created_book['id']}").status_code == 404


def test_search_books_by_title_author_and_category(
    client: TestClient,
    created_book: dict[str, object],
) -> None:
    assert client.get("/books/search?title=HOBBIT").json() == [created_book]
    assert client.get("/books/search?author=tolkien").json() == [created_book]
    assert client.get("/books/search?category=fant").json() == [created_book]
    assert client.get("/books/search?title=unknown").json() == []
    assert client.get("/books/search").status_code == 422


def test_book_validation_and_unknown_ids(
    client: TestClient,
    book_payload: dict[str, str],
) -> None:
    invalid = {**book_payload, "title": " "}
    assert client.post("/books", json=invalid).status_code == 422
    assert client.post(
        "/books",
        json={**book_payload, "title": "T" * 201},
    ).status_code == 422
    assert client.get("/books/999").status_code == 404
    assert client.put("/books/999", json=book_payload).status_code == 404
    assert client.delete("/books/999").status_code == 404


def test_book_with_lending_history_cannot_be_deleted(
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
    )
    assert issue.status_code == 201

    response = client.delete(f"/books/{created_book['id']}")
    assert response.status_code == 409
