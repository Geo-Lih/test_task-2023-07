from datetime import date, datetime
from typing import List, Union

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field
from decimal import Decimal


class BaseCustomModel(BaseModel):
    class Config:
        orm_mode = True


class CreditBase(BaseCustomModel):
    issuance_date: date
    is_closed: bool


class CreditBaseTrue(CreditBase):
    actual_return_date: date
    body: int
    percent: Decimal
    payments_sum: Decimal


class CreditBaseFalse(CreditBase):
    return_date: date
    overdue_days: int
    body: int
    percent: Decimal
    body_payment_sum: Decimal
    percent_payment_sum: Decimal


class CreditResponse(BaseModel):
    data: List[Union[CreditBaseTrue, CreditBaseFalse]]


class PlansBase(BaseCustomModel):
    period: date
    sum: int = Field(..., ge=0)
    category_id: int

    @validator('period', pre=True)
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%Y.%m.%d").date()
        return v

    @validator('period')
    def validate_day(cls, v):
        if v.day != 1:
            raise HTTPException(status_code=422, detail="Should be the first day of month")
        return v


class PlansPerformanceBase(BaseCustomModel):
    month: int
    category: int
    sum: Decimal
    percentage: float


class PlansPerformanceIssuance(PlansPerformanceBase):
    credits_sum: Decimal


class PlansPerformanceCollection(PlansPerformanceBase):
    payments_sum: Decimal


class PlansPerformanceResponse(BaseModel):
    data: List[Union[PlansPerformanceIssuance, PlansPerformanceCollection]]


class YearPerformance(BaseCustomModel):
    year_and_month: str
    amount_of_issuance: int
    issuance_plan_sum: float
    issuance_sum: float
    percentage_of_issuance: float
    amount_of_payments: int
    payments_plan_sum: float
    payments_sum: float
    percentage_of_payments: float
    percentage_of_issuance_per_year: float
    percentage_of_payments_per_year: float


class YearPerformanceResponse(BaseModel):
    data: List[YearPerformance]
