from fastapi import APIRouter, Depends, HTTPException 
from sqlmodel import Session, select
from app.database import get_db
from app.tasks.models import Tasks , TaskCreate, TaskResponse, User , TaskPatch ,TaskUpdate
from app.auth.security import get_current_active_user
from app.tasks.Filter import FilterTask , FilterParams
from app.tasks.sort import SortTask
router = APIRouter(prefix="/tasks", tags=["tasks"])
from sqlmodel import or_ , asc , desc , col


@router.post("/create", response_model=TaskResponse)
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

@router.get("/my", response_model=list[TaskResponse])
async def get_my_tasks(
    search: str | None = None,
    db: Session = Depends(get_db),
    filter_query: FilterTask = Depends(),
    pagination: FilterParams = Depends(),
    sort_query: SortTask = SortTask.desc, 
    current_user: User = Depends(get_current_active_user),
):
    statement = select(Tasks).where(Tasks.owner_id == current_user.id)

    if search:
        statement = statement.where(
            or_(
                col(Tasks.title).contains(search),
                col(Tasks.description).contains(search)
            )
        )

    if filter_query.is_done is not None:
        statement = statement.where(Tasks.is_done == filter_query.is_done)

    if filter_query.priority is not None:
        statement = statement.where(Tasks.priority == filter_query.priority)

    order_func = asc if sort_query == SortTask.asc else desc
    statement = statement.order_by(order_func(Tasks.id)) 

    statement = statement.offset(pagination.offset).limit(pagination.limit)

    results = db.exec(statement).all()
    return results

@router.get("/get/{task_id}", response_model=TaskResponse)
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

@router.put("/update/{task_id}", response_model=TaskResponse)
def update_task_put(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):

    task = db.exec(
        select(Tasks).where(
            Tasks.id == task_id,
            Tasks.owner_id == current_user.id
        )
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.title = task_data.title
    task.description = task_data.description
    task.done = task_data.done

    db.add(task)
    db.commit()
    db.refresh(task)

    return task

@router.patch("/update/{task_id}", response_model=TaskResponse)
def patch_task(
    task_id: int,
    task_data: TaskPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):

    task = db.exec(
        select(Tasks).where(
            Tasks.id == task_id,
            Tasks.owner_id == current_user.id
        )
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task, key, value)

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.delete("/delete/{task_id}", status_code=204)
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

print("TASK ROUTER LOADED")