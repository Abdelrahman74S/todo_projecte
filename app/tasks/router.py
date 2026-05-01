from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_db
from app.tasks.models import Tasks , TaskCreate, TaskResponse, User
from app.auth.security import get_current_active_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    new_task = Tasks(**task_data.model_dump(), owner_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return new_task


@router.get("/", response_model=list[TaskResponse])
def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    statement = select(Tasks).where(Tasks.owner_id == current_user.id)
    results = db.exec(statement).all()
    return results