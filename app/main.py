from fastapi import FastAPI
from app.auth.auth import router as auth_router
from app.database import create_db_and_tables , Session
from app.tasks.router import router as tasks_router

app = FastAPI(
    title="To-Do List API",
    description="بداية مشروع الـ To-Do بإستخدام FastAPI و SQLModel",
    version="1.0.0"
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(auth_router)
app.include_router(tasks_router)

@app.get("/")
def root():
    return {"message": "Welcome to the To-Do API! Go to /docs to see the Swagger UI."}