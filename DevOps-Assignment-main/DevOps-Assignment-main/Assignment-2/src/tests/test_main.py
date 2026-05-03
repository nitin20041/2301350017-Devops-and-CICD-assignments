from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_todo():
    response = client.post("/todos", json={"title": "Test Todo", "done": False})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["done"] is False
    assert "id" in data

def test_get_todos():
    # Ensure there's at least one todo
    client.post("/todos", json={"title": "List Todo", "done": False})
    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(t["title"] == "List Todo" for t in data)

def test_update_todo():
    # Create one first
    create_res = client.post("/todos", json={"title": "Old Title", "done": False})
    todo_id = create_res.json()["id"]
    
    response = client.put(f"/todos/{todo_id}", json={"title": "New Title", "done": True})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["done"] is True

def test_delete_todo():
    create_res = client.post("/todos", json={"title": "To Delete", "done": False})
    todo_id = create_res.json()["id"]
    
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204
    
    # Verify it's gone
    get_res = client.get("/todos")
    assert all(t["id"] != todo_id for t in get_res.json())
