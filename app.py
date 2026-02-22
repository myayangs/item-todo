from flask import Flask, render_template, request, redirect, url_for
import json, os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "todos.json")


def parse_due_display(due_at: str | None):
    """
    due_at format dari input datetime-local: 'YYYY-MM-DDTHH:MM'
    Return string display: 'DD Mon YYYY, HH:MM'
    """
    if not due_at:
        return None
    try:
        dt = datetime.strptime(due_at, "%Y-%m-%dT%H:%M")
        return dt.strftime("%d %b %Y, %H:%M")
    except ValueError:
        return None


def load_todos():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            todos = json.load(f)
        except json.JSONDecodeError:
            return []

    # Backward-compatible defaults
    for t in todos:
        t.setdefault("completed", False)
        t.setdefault("priority", "Medium")
        t.setdefault("due_at", None)
        t.setdefault("due_display", parse_due_display(t.get("due_at")))
    return todos


def save_todos(todos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


@app.get("/")
def index():
    todos = load_todos()
    edit_id = request.args.get("edit", default=None, type=int)

    # Optional: sorting biar yang punya jadwal muncul duluan (jadwal terdekat di atas)
    def sort_key(t):
        due = t.get("due_at")
        return (0, due) if due else (1, "")
    todos = sorted(todos, key=sort_key)

    return render_template("index.html", todos=todos, edit_id=edit_id)


@app.post("/add")
def add():
    task = request.form.get("task", "").strip()
    priority = request.form.get("priority", "Medium")
    due_at = request.form.get("due_at")  # contoh: '2026-02-19T02:00' (boleh None)

    if not task:
        return redirect(url_for("index"))

    todos = load_todos()
    next_id = max([t["id"] for t in todos], default=0) + 1

    todos.append({
        "id": next_id,
        "task": task,
        "priority": priority,
        "completed": False,
        "due_at": due_at,
        "due_display": parse_due_display(due_at)
    })

    save_todos(todos)
    return redirect(url_for("index"))


@app.post("/toggle/<int:todo_id>")
def toggle(todo_id):
    todos = load_todos()
    for t in todos:
        if t["id"] == todo_id:
            t["completed"] = not t.get("completed", False)
            break
    save_todos(todos)
    return redirect(url_for("index"))


@app.post("/delete/<int:todo_id>")
def delete(todo_id):
    todos = load_todos()
    todos = [t for t in todos if t["id"] != todo_id]
    save_todos(todos)
    return redirect(url_for("index"))


@app.post("/edit/<int:todo_id>")
def edit(todo_id):
    new_task = request.form.get("task", "").strip()
    new_priority = request.form.get("priority", "Medium")
    new_due_at = request.form.get("due_at")  # ambil jadwal baru dari form edit

    if not new_task:
        return redirect(url_for("index"))

    todos = load_todos()
    for t in todos:
        if t["id"] == todo_id:
            t["task"] = new_task
            t["priority"] = new_priority
            t["due_at"] = new_due_at
            t["due_display"] = parse_due_display(new_due_at)
            break

    save_todos(todos)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
