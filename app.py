"""Coffee Rating App (task3)
Run:  pip install flask  &&  python app.py   ->  http://127.0.0.1:5000
"""
import sqlite3
from flask import Flask, g, jsonify, render_template_string, abort

DB = "coffee.db"
app = Flask(__name__)

SEED = [
    ("Ethiopia Yirgacheffe", "Floral, bergamot, light roast"),
    ("Colombia Huila", "Caramel, red apple, medium roast"),
    ("Sumatra Mandheling", "Earthy, cocoa, dark roast"),
    ("Kenya AA", "Blackcurrant, citrus, bright acidity"),
    ("Monsooned Malabar", "Spicy, low acid, heavy body"),
]


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_):
    conn = g.pop("db", None)
    if conn:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS coffees (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL UNIQUE,
               notes TEXT NOT NULL,
               votes INTEGER NOT NULL DEFAULT 0 CHECK (votes >= 0)
           )"""
    )
    conn.executemany("INSERT OR IGNORE INTO coffees (name, notes) VALUES (?, ?)", SEED)
    conn.commit()
    conn.close()


def all_coffees():
    rows = db().execute("SELECT id, name, notes, votes FROM coffees ORDER BY votes DESC, name").fetchall()
    return [dict(r) for r in rows]


@app.get("/api/coffees")
def list_coffees():
    return jsonify(all_coffees())


@app.post("/api/coffees/<int:coffee_id>/vote")
def vote(coffee_id):
    conn = db()
    # Atomic increment in SQL: no read-modify-write, so concurrent clicks don't lose votes.
    cur = conn.execute("UPDATE coffees SET votes = votes + 1 WHERE id = ?", (coffee_id,))
    conn.commit()
    if cur.rowcount == 0:
        abort(404, description="Coffee not found")
    return jsonify(all_coffees())


@app.errorhandler(404)
def not_found(e):
    return jsonify(error=e.description), 404


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Coffee votes</title>
<style>
  :root { --bg:#f3ede4; --ink:#2a1d14; --muted:#7a6a5c; --line:#d9cdbd; --accent:#3f6b5a; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--ink); font:17px/1.5 Georgia, "Times New Roman", serif; }
  main { max-width:620px; margin:0 auto; padding:48px 20px; }
  h1 { font-size:2rem; margin:0 0 4px; }
  p.sub { color:var(--muted); margin:0 0 28px; }
  ul { list-style:none; margin:0; padding:0; }
  li { display:flex; align-items:center; gap:16px; padding:16px 0; border-top:1px solid var(--line); }
  li:last-child { border-bottom:1px solid var(--line); }
  .info { flex:1; min-width:0; }
  .name { font-weight:bold; }
  .notes { color:var(--muted); font-size:.9rem; }
  .count { font-size:1.5rem; min-width:2.5ch; text-align:right; font-variant-numeric:tabular-nums; }
  button { font:inherit; padding:8px 16px; border:2px solid var(--accent); background:transparent;
           color:var(--accent); border-radius:4px; cursor:pointer; }
  button:hover { background:var(--accent); color:#fff; }
  button:focus-visible { outline:3px solid var(--ink); outline-offset:2px; }
  button:disabled { opacity:.5; cursor:wait; }
  #err { color:#a33; min-height:1.5em; }
</style></head>
<body><main>
  <h1>Which coffee wins?</h1>
  <p class="sub">Vote as often as you like. Counts are saved in the database.</p>
  <p id="err" role="alert"></p>
  <ul id="list"></ul>
</main>
<script>
const list = document.getElementById("list"), err = document.getElementById("err");

function render(items) {
  list.replaceChildren(...items.map(c => {
    const li = document.createElement("li");
    li.innerHTML = '<div class="info"><div class="name"></div><div class="notes"></div></div>' +
                   '<div class="count" aria-live="polite"></div><button>Vote</button>';
    li.querySelector(".name").textContent = c.name;      // textContent: no HTML injection
    li.querySelector(".notes").textContent = c.notes;
    li.querySelector(".count").textContent = c.votes;
    const btn = li.querySelector("button");
    btn.setAttribute("aria-label", "Vote for " + c.name);
    btn.onclick = () => vote(c.id, btn);
    return li;
  }));
}

async function load() {
  try {
    const r = await fetch("/api/coffees");
    if (!r.ok) throw new Error();
    render(await r.json());
  } catch { err.textContent = "Couldn't load coffees. Refresh the page."; }
}

async function vote(id, btn) {
  btn.disabled = true; err.textContent = "";
  try {
    const r = await fetch("/api/coffees/" + id + "/vote", { method: "POST" });
    if (!r.ok) throw new Error();
    render(await r.json());
  } catch { err.textContent = "Vote not saved. Try again."; btn.disabled = false; }
}
load();
</script></body></html>"""


@app.get("/")
def index():
    return render_template_string(PAGE)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
