from fastapi_mail import ConnectionConfig

mail_conf = ConnectionConfig(
    MAIL_USERNAME="alsynmamlk@gmail.com",
    MAIL_PASSWORD="qyou ddhf wzba pmaw",
    MAIL_FROM="alsynmamlk@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)