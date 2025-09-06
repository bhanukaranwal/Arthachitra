from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps."""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class UUIDMixin:
    """Mixin to add UUID primary key."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
