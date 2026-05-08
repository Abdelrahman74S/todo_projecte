from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from sqlalchemy import func # تأكد من استيراد func من sqlalchemy

class TimestampMixin(SQLModel):
    # Set when the row is first created
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            "server_default": func.now() # يخبر قاعدة البيانات بوضع الوقت الحالي كافتراضي
        },
        nullable=False
    )
    
    # Set at creation AND updated automatically on any change
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            "server_default": func.now(), # للسجلات القديمة والجديدة
            "onupdate": func.now()        # يتحدث تلقائياً عند أي تعديل
        },
        nullable=False
    )