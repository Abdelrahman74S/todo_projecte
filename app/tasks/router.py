from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_db
from app.tasks.models import Tasks , TaskCreate, TaskResponse, User
from app.auth.security import get_current_active_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task(
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
async def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    statement = select(Tasks).where(Tasks.owner_id == current_user.id)
    results = db.exec(statement).all()
    return results

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    statement = select(Tasks).where(Tasks.id == task_id, Tasks.owner_id == current_user.id)
    result = db.exec(statement).first()
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    statement = select(Tasks).where(Tasks.id == task_id, Tasks.owner_id == current_user.id)
    result = db.exec(statement).first()
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    
    for key, value in task_data.model_dump().items():
        setattr(result, key, value)
    
    db.add(result)
    db.commit()
    db.refresh(result)
    
    return result

@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    statement = select(Tasks).where(Tasks.id == task_id, Tasks.owner_id == current_user.id)
    result = db.exec(statement).first()
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(result)
    db.commit()
