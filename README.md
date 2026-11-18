# Coffee Rating App (task3)

A small web app that lists coffees and lets users vote for them with a button. Every click increments a vote count stored in a SQLite database.

## Tech stack

- Python 3.8+
- Flask (backend and API)
- SQLite (built into Python, no setup needed)
- Plain HTML, CSS and JavaScript (served by Flask from `app.py`)

## Setup and run

```bash
pip install flask
python app.py
```

Open http://127.0.0.1:5000 in your browser.

On first run, `coffee.db` is created next to `app.py` and seeded with five coffees. To reset all votes, stop the app and delete `coffee.db`.

## Project structure

```
coffee_rating/
├── app.py        # Flask app, database logic, API routes, HTML page
├── coffee.db     # created on first run
└── README.md
```

## Database

Table `coffees`:

| Column  | Type    | Notes                              |
|---------|---------|------------------------------------|
| id      | INTEGER | Primary key, auto-increment        |
| name    | TEXT    | Unique, not null                   |
| notes   | TEXT    | Tasting notes, not null            |
| votes   | INTEGER | Default 0, `CHECK (votes >= 0)`    |

## API

| Method | Endpoint                       | Description                                           |
|--------|--------------------------------|-------------------------------------------------------|
| GET    | `/`                            | The voting page                                       |
| GET    | `/api/coffees`                 | All coffees as JSON, sorted by votes (highest first)  |
| POST   | `/api/coffees/<id>/vote`       | Adds one vote to the coffee, returns the updated list |

An unknown `<id>` returns `404` with `{"error": "Coffee not found"}`.

Example:

```bash
curl -X POST http://127.0.0.1:5000/api/coffees/1/vote
```

## How voting works

1. The user clicks **Vote** on a coffee.
2. The browser sends `POST /api/coffees/<id>/vote`.
3. The server runs one atomic statement:
   `UPDATE coffees SET votes = votes + 1 WHERE id = ?`
4. The server returns the updated list, and the page re-renders with the new counts and order.

The increment happens inside SQL rather than reading the count into Python and writing it back, so simultaneous clicks cannot overwrite each other.

## Known limitations

- **No vote limiting.** The same user can vote unlimited times. A real app needs per-user or per-IP limits, or a voters table with a unique constraint on (voter, coffee).
- **Upvotes only.** There are no 1-5 star ratings or averages.
- **Development setup.** SQLite with a connection per request suits a demo, not heavy concurrent writes. `debug=True` in `app.py` must be turned off in production.
- **Not auto-tested.** There is no test suite included.

## Possible extensions

- Add user accounts or cookie-based vote tracking
- Add a form to submit new coffees
- Switch to star ratings (store each rating, compute the average)
- Add automated tests with `pytest` and Flask's test client
