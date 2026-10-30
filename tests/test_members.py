"""Tests for member management endpoints."""

from fastapi.testclient import TestClient


def test_register_and_list_members(
    client: TestClient,
    member_payload: dict[str, str],
) -> None:
    created = client.post("/members", json=member_payload)

    assert created.status_code == 201
    assert created.json() == {"id": 1, **member_payload}
    assert client.get("/members").json() == [created.json()]


def test_get_update_and_delete_member(
    client: TestClient,
    created_member: dict[str, object],
) -> None:
    assert client.get(f"/members/{created_member['id']}").json() == created_member

    updated = {
        "full_name": "Asha R.",
        "email": "asha.r@example.com",
        "phone": None,
    }
    update_response = client.put(
        f"/members/{created_member['id']}",
        json=updated,
    )
    assert update_response.status_code == 200
    assert update_response.json() == {"id": created_member["id"], **updated}

    delete_response = client.delete(f"/members/{created_member['id']}")
    assert delete_response.status_code == 204
    assert client.get(f"/members/{created_member['id']}").status_code == 404


def test_member_validation_duplicate_email_and_unknown_ids(
    client: TestClient,
    member_payload: dict[str, str],
    created_member: dict[str, object],
) -> None:
    invalid = {**member_payload, "email": "not-an-email"}
    assert client.post("/members", json=invalid).status_code == 422
    assert client.post("/members", json=member_payload).status_code == 409
    assert client.get("/members/999").status_code == 404
    assert client.put("/members/999", json=member_payload).status_code == 404
    assert client.delete("/members/999").status_code == 404
    assert client.get("/members/999/issues").status_code == 404


def test_member_with_lending_history_cannot_be_deleted(
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

    delete_response = client.delete(f"/members/{created_member['id']}")
    assert delete_response.status_code == 409
