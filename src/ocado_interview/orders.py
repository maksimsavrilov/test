from enum import Enum
from decimal import Decimal
from typing import List
from sqlalchemy import CheckConstraint, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM as pgEnum
from pydantic import BaseModel, field_validator
from datetime import datetime


class Base(DeclarativeBase):
    pass

class Order(BaseModel):
    order_id: str
    customer_id: int
    amount: Decimal
    currency: str
    status: str
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
        if len(value) != 3:
            raise ValueError('Currency must be a 3-letter code')
        return value

    @field_validator('status')
    def check_status(cls, value):
        valid_statuses = ['pending', 'completed', 'cancelled']
        if value not in valid_statuses:
            raise ValueError(f'Status must be one of {valid_statuses}')
        return value

    # @field_validator('created_at')
    # def check_created_at(cls, value):
    #     # Here you can add validation for the created_at field, e.g., check if it's a valid datetime string
    #     # For example, you could use datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
    #     try:
    #         datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
    #     except ValueError:
    #         raise ValueError('created_at must be a valid datetime string in the format YYYY-MM-DDTHH:MM:SS')
    #     return value

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

class OrderModel(Base):
    __tablename__ = 'orders'

    order_id: Mapped[str] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column()
    amount: Mapped[Decimal] = mapped_column(CheckConstraint("amount > 0", name="check_amount_positive"))
    currency: Mapped[str] = mapped_column()
    status: Mapped[OrderStatus] = mapped_column(OrderStatusType)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))