import pytest

from app import app, seed


@pytest.fixture
def client():
    seed()  # start every test from the same sample data
    return app.test_client()


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_books_returns_list_with_expected_fields(client):
    response = client.get("/books")
    assert response.status_code == 200
    books = response.get_json()
    assert isinstance(books, list)
    assert len(books) == 3
    assert set(books[0]) == {"id", "title", "author", "status"}


def test_add_book_then_find_it_in_list(client):
    response = client.post("/books", json={"title": "Dune", "author": "Frank Herbert"})
    assert response.status_code == 201
    titles = [b["title"] for b in client.get("/books").get_json()]
    assert "Dune" in titles


def test_unknown_url_returns_404(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404