# API de Lista de Tareas Interactiva con Python y Flask

API REST minimal con 3 endpoints:

- **GET /todos** ? lista de tareas ([{ done: bool, label: string }])
- **POST /todos** ? agrega una tarea (body: { "done": true, "label": "Sample Todo 3" }) y devuelve la lista
- **DELETE /todos/<position>** ? elimina por índice (0-based) y devuelve la lista

## Requisitos
- Python 3.10+ (probado en 3.13)
- pip

## Instalación
`ash
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py

# GET
curl.exe http://127.0.0.1:5000/todos

# POST (usa archivo para evitar comillas en PowerShell)
# Crear body.json:
# { "done": true, "label": "Sample Todo 3" }
curl.exe -X POST "http://127.0.0.1:5000/todos" -H "Content-Type: application/json" --data-binary "@body.json"

# DELETE (posición 0)
curl.exe -X DELETE "http://127.0.0.1:5000/todos/0"


(redeploy)
