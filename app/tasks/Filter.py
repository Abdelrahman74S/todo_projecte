from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from datetime import UTC, datetime
from typing import Optional, List
from fastapi import  Query 
from app.tasks.enum import TaskPriority

# from fastapi_filter.contrib.sqlalchemy import Filter

class FilterTask(SQLModel):
    is_done: bool | None = None
    priority: TaskPriority | None = None


class FilterParams(SQLModel):
    limit: int = Field(default=100, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    order_by: str = "created_at"