from app.tasks.enum import TaskPriority
from sqlmodel import SQLModel, Field

class FilterParams(SQLModel):
    limit: int = 100
    offset: int = 0

class FilterTask(SQLModel):
    is_done: bool | None = None
    priority: TaskPriority | None = None