from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(max_length=255)
    email: EmailStr = Field(unique=True)
    password: str = Field(min_length=8, max_length=200)
    age: int | None = None
    is_active: bool = True
    created_at: datetime | None = None
    tasks: list["Tasks"] = Relationship(back_populates="owner")

class Tasks(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
    owner_id: int = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="tasks")