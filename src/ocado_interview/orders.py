from enum import Enum
from decimal import Decimal
from typing import List
from sqlalchemy import CheckConstraint, DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM as pgEnum
from pydantic import BaseModel, field_validator
from datetime import datetime
import re


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
    order_id: str
    customer_id: int
    amount: Decimal
    currency: str
    status: OrderStatus
    created_at: datetime

    @field_validator('order_id')
    def check_order_id(cls, value):
        if len(value) == 0:
            raise ValueError('Order ID can not be empty')
        if len(value) > 50:
            raise ValueError('Order ID can not be longer than 50 characters')
        return value

    @field_validator('customer_id')
    def check_customer_id(cls, value):
        if value <= 0:
            raise ValueError('Customer ID must be a positive integer')
        return value

    @field_validator('amount')
    def check_amount(cls, value):
        if value <= 0:
            raise ValueError('Amount must be a positive decimal')
        return value

    @field_validator('currency')
    def check_currency(cls, value):
        if not re.match(r'^[A-Z]{3}$', value):
            raise ValueError('Currency must be a 3-letter code')
        return value
    
    @field_validator("created_at")
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