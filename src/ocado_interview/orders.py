from dataclasses import Field
from enum import Enum
from decimal import Decimal
from sqlalchemy import CheckConstraint, DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM as pgEnum
from pydantic import BaseModel, field_validator
from datetime import datetime


class Base(DeclarativeBase):
    pass

class OrderStatus(str, Enum):
    pending = 'pending'
    completed = 'completed'
    cancelled = 'cancelled'

OrderStatusType: pgEnum = pgEnum(
    OrderStatus,
    name="order_status",
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)

class Order(BaseModel):
    order_id: str = Field(..., min_length=1, max_length=50, description="Order ID must be a non-empty string with a maximum length of 50 characters")
    customer_id: int = Field(..., gt=0, description="Customer ID must be a positive integer")
    amount: Decimal = Field(..., gt=0, description="Amount must be a positive decimal")
    currency: str = Field(..., description="Currency must be a 3-letter code", regex=r'^[A-Z]{3}$')
    status: OrderStatus = Field(..., description="Status must be one of 'pending', 'completed', or 'cancelled'")
    created_at: datetime = Field(..., description="Created_at timestamp must be timezone-aware")

    
    @field_validator('created_at')
    def check_created_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        return value


class OrderModel(Base):
    __tablename__ = 'orders'

    order_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    customer_id: Mapped[int] = mapped_column(CheckConstraint("customer_id > 0", name="check_customer_id_positive"))
    amount: Mapped[Decimal] = mapped_column(CheckConstraint("amount > 0", name="check_amount_positive"))
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[OrderStatus] = mapped_column(OrderStatusType)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))