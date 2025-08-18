from flask import Flask, request, jsonify, abort, send_from_directory
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Boolean, select
from sqlalchemy.orm import sessionmaker, declarative_base
import os

app = Flask(__name__)
# CORS abierto para pruebas (luego puedes restringir orígenes)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- BD: por defecto SQLite local; si hay DATABASE_URL en el entorno, la usa ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///todos.db")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String, nullable=False)
    done = Column(Boolean, nullable=False, default=False)

# Crea la tabla si no existe
Base.metadata.create_all(engine)

# --- API /todos ---
@app.get("/todos")
def get_todos():
    with SessionLocal() as db:
        rows = db.execute(select(Todo).order_by(Todo.id.asc())).scalars().all()
        return jsonify([{"done": r.done, "label": r.label} for r in rows]), 200

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

    with SessionLocal() as db:
        db.add(Todo(label=label, done=data["done"]))
        db.commit()
        rows = db.execute(select(Todo).order_by(Todo.id.asc())).scalars().all()
        return jsonify([{"done": r.done, "label": r.label} for r in rows]), 201

@app.delete("/todos/<int:position>")
def delete_todo(position):
    with SessionLocal() as db:
        rows = db.execute(select(Todo).order_by(Todo.id.asc())).scalars().all()
        if position < 0 or position >= len(rows):
            abort(404, description="No existe un todo en esa posición")
        db.delete(rows[position])
        db.commit()
        rows = db.execute(select(Todo).order_by(Todo.id.asc())).scalars().all()
        return jsonify([{"done": r.done, "label": r.label} for r in rows]), 200

# --- UI estática ---
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")

@app.get("/")
def root():
    # sirve el front en la raíz
    return send_from_directory(PUBLIC_DIR, "index.html")

@app.get("/health")
def health():
    return jsonify({"ok": True}), 200

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

@app.errorhandler(500)
def server_error(e):
    return jsonify(error="server_error", message="Ocurrió un error en el servidor"), 500

if __name__ == "__main__":
    app.run(debug=True)
