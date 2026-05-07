from fastapi import Depends, HTTPException, APIRouter, status
from app.database import Session
from sqlmodel import select 
from app.database import get_db
from app.tasks.models import (
    User, UserCreate, UserResponse, Token,
    ProfileUser, UpdateProfileUser,
    ProfileUserResponse
)
from app.auth.security import DUMMY_HASH, create_access_token, get_password_hash, verify_password , get_current_active_user
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, db: Session = Depends(get_db)):
    statement = select(User).where(User.email == user_create.email)
    existing_user = db.exec(statement).first() 
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User already registered"
        )

    hashed_password = get_password_hash(user_create.password)

    user_data = user_create.model_dump()
    user_data["password"] = hashed_password
    
    new_user = User(**user_data)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user) 

    return new_user

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    statement = select(User).where(User.email == user_credentials.username)
    user = db.exec(statement).first()
    if not user:
        verify_password(user_credentials.password, DUMMY_HASH)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
    
    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
    
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=ProfileUserResponse, status_code=status.HTTP_200_OK)
async def profile_user(
    current_user: User = Depends(get_current_active_user),
):

    return 

@router.patch("/profile/update",response_model=ProfileUserResponse,status_code=status.HTTP_200_OK
)
async def update_user(
    user_data: UpdateProfileUser,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):

    update_data = user_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user
