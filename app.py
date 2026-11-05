import os

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Injected by the pipeline later (commit SHA). "dev" when running locally.
APP_VERSION = os.environ.get("APP_VERSION", "dev")
STATUSES = ("to-read", "reading", "finished")

books = []
_next_id = 1


def seed():
    """Reset the in-memory list to a small set of sample books."""
    global books, _next_id
    books = [
        {"id": 1, "title": "The Phoenix Project", "author": "Gene Kim", "status": "finished"},
        {"id": 2, "title": "Site Reliability Engineering", "author": "Betsy Beyer", "status": "reading"},
        {"id": 3, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "status": "to-read"},
    ]
    _next_id = 4


seed()


@app.get("/")
def index():
    return render_template("index.html", version=APP_VERSION)


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/version")
def version():
    return jsonify(version=APP_VERSION)


@app.get("/books")
def list_books():
    status = request.args.get("status")
    if status:
        return jsonify([b for b in books if b["status"] == status])
    return jsonify(books)


@app.post("/books")
def add_book():
    global _next_id
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    author = str(data.get("author", "")).strip()
    status = data.get("status", "to-read")
    if not title or not author:
        return jsonify(error="title and author are required"), 400
    if status not in STATUSES:
        return jsonify(error=f"status must be one of {list(STATUSES)}"), 400
    book = {"id": _next_id, "title": title, "author": author, "status": status}
    _next_id += 1
    books.append(book)
    return jsonify(book), 201


@app.patch("/books/<int:book_id>")
def update_status(book_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in STATUSES:
        return jsonify(error=f"status must be one of {list(STATUSES)}"), 400
    for book in books:
        if book["id"] == book_id:
            book["status"] = status
            return jsonify(book)
    return jsonify(error="book not found"), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
