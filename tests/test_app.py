"""Application documentation and database persistence checks."""

from fastapi.testclient import TestClient


def test_swagger_and_all_api_routes_are_available(client: TestClient) -> None:
    docs_response = client.get("/docs")
    openapi_response = client.get("/openapi.json")

    assert docs_response.status_code == 200
    assert "text/html" in docs_response.headers["content-type"]
    assert b"SwaggerUIBundle" in docs_response.content
    assert openapi_response.status_code == 200

    paths = openapi_response.json()["paths"]
    assert {"/books", "/books/search", "/books/{book_id}"} <= paths.keys()
    assert {"/members", "/members/{member_id}", "/members/{member_id}/issues"} <= paths.keys()
    assert {"/issues", "/issues/{issue_id}/return"} <= paths.keys()
    assert set(paths["/books"]) == {"get", "post"}
    assert set(paths["/books/{book_id}"]) == {"get", "put", "delete"}
    assert set(paths["/members"]) == {"get", "post"}
    assert set(paths["/members/{member_id}"]) == {"get", "put", "delete"}
    assert set(paths["/issues"]) == {"get", "post"}
    assert set(paths["/issues/{issue_id}/return"]) == {"post"}


def test_root_redirects_to_swagger(client: TestClient) -> None:
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/docs"
