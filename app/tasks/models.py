from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from datetime import UTC, datetime
from typing import Optional, List
from app.tasks.enum import TaskPriority

class UserBase(SQLModel):
    username: str = Field(max_length=255)
    email: EmailStr = Field(unique=True, index=True)
    age: Optional[int] = None

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str = Field(min_length=8, max_length=200)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    tasks: List["Tasks"] = Relationship(back_populates="owner")

class UserCreate(UserBase):
    password: str

class UserUpdate(SQLModel): 
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    age: Optional[int] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

# --- Token ---
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(SQLModel):
    sub: str
    exp: Optional[int] = None

# --- Task Models ---
class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None


class Tasks(TaskBase, table=True):
    __tablename__ = "user_tasks"

    id: int | None = Field(default=None, primary_key=True)

    is_done: bool = Field(default=False)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None

    owner_id: int = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="tasks")


class TaskCreate(TaskBase):
    priority: TaskPriority = TaskPriority.MEDIUM

class TaskUpdate(SQLModel):
    title: str
    description: str | None = None
    is_done: bool
    priority: TaskPriority

class TaskResponse(TaskBase):
    id: int
    owner_id: int
    is_done: bool
    priority: TaskPriority
    created_at: datetime

class TaskPatch(SQLModel):
    title: str | None = None
    description: str | None = None
    is_done: bool | None = None
    priority: TaskPriority | None = None
    
