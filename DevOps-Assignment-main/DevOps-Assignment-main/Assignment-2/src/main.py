import os
import time
import logging
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pythonjsonlogger import jsonlogger
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# --- Logging Setup ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logger = logging.getLogger("todo-api")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(method)s %(path)s %(status)s %(latency)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(LOG_LEVEL)

# --- Metrics Setup ---
REQUEST_COUNT = Counter(
    'http_requests_total', 'Total HTTP Requests',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 'HTTP Request Latency',
    ['method', 'endpoint']
)

# --- Database Setup ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/todos.db")
# Ensure the data directory exists
os.makedirs("./data", exist_ok=True)
# SQLite specific handling for concurrent access
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TodoItem(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    done = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="StackForge To-Do API")

# --- Middleware for Logging & Metrics ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    # Update Metrics
    REQUEST_COUNT.labels(
        method=request.method, 
        endpoint=request.url.path, 
        http_status=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(
        method=request.method, 
        endpoint=request.url.path
    ).observe(process_time / 1000)

    # Structured Logging
    log_extra = {
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "latency": f"{process_time:.2f}ms"
    }
    
    if response.status_code >= 400:
        logger.error("Request failed", extra=log_extra)
    else:
        logger.info("Request processed", extra=log_extra)
        
    return response

# --- Endpoints ---

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/todos", response_model=List[dict])
def get_todos(db: Session = Depends(get_db)):
    todos = db.query(TodoItem).all()
    return [{"id": t.id, "title": t.title, "done": t.done} for t in todos]

@app.post("/todos", status_code=201)
def create_todo(todo: dict, db: Session = Depends(get_db)):
    if "title" not in todo:
        raise HTTPException(status_code=400, detail="Title is required")
    new_todo = TodoItem(title=todo["title"], done=todo.get("done", False))
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return {"id": new_todo.id, "title": new_todo.title, "done": new_todo.done}

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: dict, db: Session = Depends(get_db)):
    db_todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if "title" in todo:
        db_todo.title = todo["title"]
    if "done" in todo:
        db_todo.done = todo["done"]
        
    db.commit()
    return {"id": db_todo.id, "title": db_todo.title, "done": db_todo.done}

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
