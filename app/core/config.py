# app/core/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "change-me-use-openssl-rand-hex-32"

    FORGET_PWD_SECRET_KEY: str = "forget-password-secret_hs3"

    ALGORITHM: str = "HS256"

    APP_HOST: str = "http://127.0.0.1:8000"

    FORGET_PASSWORD_URL: str = "/reset-password"

    FORGET_PASSWORD_LINK_EXPIRE_MINUTES: int = 10

    MAIL_FROM_NAME: str = "Todo App Abdo"


settings = Settings()