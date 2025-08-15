from flask import Flask, request, jsonify, abort, send_from_directory
from flask_cors import CORS
import json, os

app = Flask(__name__)
CORS(app)  # habilita CORS

# --- Persistencia JSON (local) ---
DATA_FILE = "todos.json"
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")

def load_todos():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_todos(items):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

# Carga inicial (seed si está vacío)
todos = load_todos()
if not todos:
    todos = [
        {"done": True, "label": "Sample Todo 1"},
        {"done": True, "label": "Sample Todo 2"},
    ]
    save_todos(todos)

# --- API ToDo ---
@app.get("/todos")
def get_todos():
    return jsonify(todos), 200

@app.post("/todos")
def add_todo():
    data = request.get_json(silent=True) or {}
    if "done" not in data or "label" not in data:
        abort(400, description='Body debe tener "done" (bool) y "label" (str)')
    if not isinstance(data["done"], bool):
        abort(400, description='"done" debe ser booleano')
    label = str(data["label"]).strip()
    if not label:
        abort(400, description='"label" no puede estar vacío')

    todo = {"done": data["done"], "label": label}
    todos.append(todo)
    save_todos(todos)
    return jsonify(todos), 201

@app.delete("/todos/<int:position>")
def delete_todo(position):
    if position < 0 or position >= len(todos):
        abort(404, description="No existe un todo en esa posición")
    todos.pop(position)
    save_todos(todos)
    return jsonify(todos), 200

# --- Raíz y health ---
@app.get("/")
def root():
    return jsonify({"ok": True, "hint": "usa /todos o /ui"}), 200

@app.get("/health")
def health():
    return jsonify({"ok": True}), 200

# --- Front estático en /ui ---
@app.get("/ui")
def ui_index():
    return send_from_directory(PUBLIC_DIR, "index.html")

@app.get("/ui/<path:filename>")
def ui_static(filename):
    return send_from_directory(PUBLIC_DIR, filename)

# --- Errores bonitos ---
@app.errorhandler(400)
def bad_request(e):
    return jsonify(error="bad_request", message=e.description), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify(error="not_found", message=e.description), 404

if __name__ == "__main__":
    app.run(debug=True)
