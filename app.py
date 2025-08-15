from flask import Flask, request, jsonify, abort, send_from_directory
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Boolean, select
from sqlalchemy.orm import sessionmaker, declarative_base
import os

app = Flask(__name__)
CORS(app)

# --------- Base de datos (Neon) ----------
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # Sube DATABASE_URL en Render → Settings → Environment
    @app.get("/")
    def missing_env():
        return jsonify({"ok": False, "error": "DATABASE_URL no configurada"}), 500

    # Evita seguir si no hay DB
    if __name__ == "__main__":
        app.run(debug=True)
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base = declarative_base()

    class Todo(Base):
        __tablename__ = "todos"
        id = Column(Integer, primary_key=True, autoincrement=True)
        label = Column(String, nullable=False)
        done = Column(Boolean, nullable=False, default=False)

    # crea la tabla si no existe
    Base.metadata.create_all(engine)

    # --------- API ToDo ----------
    @app.get("/todos")
    def get_todos():
        with SessionLocal() as db:
            rows = db.execute(select(Todo).order_by(Todo.id.asc())).scalars().all()
            data = [{"done": r.done, "label": r.label} for r in rows]
            return jsonify(data), 200

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
            data = [{"done": r.done, "label": r.label} for r in rows]
            return jsonify(data), 201

    @app.delete("/todos/<int:position>")
    def delete_todo(position):
        with SessionLocal() as db:
            rows = db.execute(select(Todo).order_by(Todo.id.asc())).scalars().all()
            if position < 0 or position >= len(rows):
                abort(404, description="No existe un todo en esa posición")
            db.delete(rows[position])
            db.commit()
            rows = db.execute(select(Todo).order_by(Todo.id.asc())).scalars().all()
            data = [{"done": r.done, "label": r.label} for r in rows]
            return jsonify(data), 200

# --------- Front y utilidades ---------
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")

@app.get("/")
def root():
    return jsonify({"ok": True, "hint": "usa /todos o /ui"}), 200

@app.get("/health")
def health():
    return jsonify({"ok": True}), 200

@app.get("/ui")
def ui_index():
    return send_from_directory(PUBLIC_DIR, "index.html")

@app.get("/ui/<path:filename>")
def ui_static(filename):
    return send_from_directory(PUBLIC_DIR, filename)

@app.errorhandler(400)
def bad_request(e):
    return jsonify(error="bad_request", message=e.description), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify(error="not_found", message=e.description), 404

if __name__ == "__main__":
    app.run(debug=True)
