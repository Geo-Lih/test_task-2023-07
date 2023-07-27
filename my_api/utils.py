import datetime
from _decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func, and_, extract
from sqlalchemy.orm import Session


def payments_sum_calculation(payments_dict, credit_db):
    payment_sum = 0
    for n in range(1, 3):
        payment_sum += payments_dict.get((credit_db.id, n), 0)
    return payment_sum


def plans_sum_calculation(db: Session, model: object, date_column: object, start_date: datetime,
                          end_date: datetime) -> Decimal:
    result = db.query(func.sum(model)).filter(
        and_(
            date_column >= start_date,
            date_column < end_date
        )
    ).scalar() or Decimal('0')
    return result


def calculate_percentage(partial: Decimal, total: Decimal) -> float:
    if total is None or total == 0:
        return 0
    percentage = round((partial / total) * 100, 1)
    return percentage


def get_count_sum_and_percentage(db: Session, model, date_field, date, sum_field, plan_sum):
    count_and_sum = db.query(
        func.count(model.id),
        func.sum(sum_field)
    ).filter(
        extract('year', date_field) == date.year,
        extract('month', date_field) == date.month
    ).first()
    count, sum_ = count_and_sum
    if count == 0 and sum_ is None:
        return 0, 0, 0
    else:
        percentage = calculate_percentage(sum_, plan_sum)
        return count, sum_, percentage


def calculate_total(db: Session, field, date_field, year):
    return db.query(
        func.sum(field)
    ).filter(
        extract('year', date_field) == year
    ).scalar()
