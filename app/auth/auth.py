from fastapi import APIRouter, Depends, status, BackgroundTasks, HTTPException
from app.database import Session
from sqlmodel import select 
from app.database import get_db
from app.tasks.models import (
    User, UserCreate, UserResponse, Token,
    ProfileUser, UpdateProfileUser,
    ProfileUserResponse
)
from app.auth.security import DUMMY_HASH, create_access_token, get_password_hash, verify_password , get_current_active_user , get_user_by_email
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_mail import FastMail, MessageSchema, MessageType
from jose import jwt ,JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.core.config import settings
from app.core.mail import mail_conf
from fastapi.responses import JSONResponse
from passlib.context import CryptContext


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



class ForgetPasswordRequest(BaseModel):
    email: str


def create_reset_password_token(email: str):
    data = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=10)
    }

    token = jwt.encode(
        data,
        settings.FORGET_PWD_SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token


@router.post("/forget-password")
async def forget_password(
    fpr: ForgetPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    user = get_user_by_email(email=fpr.email, db=db)

    if user:
        secret_token = create_reset_password_token(user.email)

        reset_link = (
            f"{settings.APP_HOST}"
            f"{settings.FORGET_PASSWORD_URL}/"
            f"{secret_token}"
        )

        email_body = {
            "company_name": settings.MAIL_FROM_NAME,
            "link_expiry_min": settings.FORGET_PASSWORD_LINK_EXPIRE_MINUTES,
            "reset_link": reset_link,
        }
    
    message = MessageSchema(
        subject="Password Reset Instructions",
        recipients=[fpr.email],
        body=f"""
        <h2>Password Reset</h2>
    
        <p>Click the link below:</p>
    
        <a href="{reset_link}">
            Reset Password
        </a>
        """,
        subtype=MessageType.html,
    )

        
    template_name = "mail/password_reset.html"
    fm = FastMail(mail_conf)
    background_tasks.add_task(
        fm.send_message,
        message,
        template_name
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": (
                "If the email exists, a password reset link has been sent."
            ),
            "success": True,
        },
    )


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


class ResetPasswordRequest(BaseModel):
    secret_token: str
    new_password: str
    confirm_password: str


class SuccessMessage(BaseModel):
    success: bool
    status_code: int
    message: str


def decode_reset_password_token(token: str):

    try:
        payload = jwt.decode(
            token,
            settings.FORGET_PWD_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        email: str | None = payload.get("sub")

        if email is None:
            return None

        return email

    except JWTError:
        return None


@router.post(
    "/reset-password",
    response_model=SuccessMessage
)
async def reset_password(
    rfp: ResetPasswordRequest,
    db: Session = Depends(get_db)
):

    email = decode_reset_password_token(
        token=rfp.secret_token
    )

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    if rfp.new_password != rfp.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    user = get_user_by_email(email=email, db=db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    hashed_password = pwd_context.hash(
        rfp.new_password
    )

    user.hashed_password = hashed_password

    db.add(user)
    db.commit()
    db.refresh(user)

    return SuccessMessage(
        success=True,
        status_code=status.HTTP_200_OK,
        message="Password reset successful!"
    )

@router.get("/reset-password/{token}")
async def reset_password_page(token: str):
    return {
        "message": "Token received",
        "token": token
    }