from flask import Flask, request, jsonify, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Estado en memoria (se pierde al reiniciar)
todos = [
    {"done": True, "label": "Sample Todo 1"},
    {"done": True, "label": "Sample Todo 2"},
]

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
    return jsonify(todos), 201

@app.delete("/todos/<int:position>")
def delete_todo(position):
    if position < 0 or position >= len(todos):
        abort(404, description="No existe un todo en esa posición")
    todos.pop(position)
    return jsonify(todos), 200

@app.errorhandler(400)
def bad_request(e):
    return jsonify(error="bad_request", message=e.description), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify(error="not_found", message=e.description), 404

if __name__ == "__main__":
    app.run(debug=True)
