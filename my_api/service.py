from collections import defaultdict
from datetime import datetime

from fastapi import UploadFile, HTTPException
from pydantic import ValidationError
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from . import utils
from . import schemas
from . import validators
from .models import Credits, Payments, Plans

import pandas as pd
from io import BytesIO
import json


def get_credits_service(user_id, db: Session):
    credits_db = db.query(Credits).filter(Credits.user_id == user_id).all()
    print(credits_db)

    credit_ids = [credit.id for credit in credits_db]
    payments = db.query(
        Payments.credit_id,
        Payments.type_id,
        func.sum(Payments.sum).label('sum')
    ).filter(Payments.credit_id.in_(credit_ids)).group_by(Payments.credit_id, Payments.type_id).all()
    print(payments)

    payments_dict = {}
    for payment in payments:
        payments_dict[(payment.credit_id, payment.type_id)] = payment.sum
    print(payments_dict)

    credits = []
    for credit_db in credits_db:
        if credit_db.actual_return_date is not None:
            payments_sum = utils.payments_sum_calculation(payments_dict, credit_db)
            credit = schemas.CreditBaseTrue(
                issuance_date=credit_db.issuance_date,
                is_closed=True,
                actual_return_date=credit_db.actual_return_date,
                body=credit_db.body,
                percent=credit_db.percent,
                payments_sum=payments_sum or 0
            )
        else:
            current_date = datetime.now().date()
            overdue_days = (current_date - credit_db.return_date).days if current_date > credit_db.return_date else 0
            body_payment_sum = payments_dict.get((credit_db.id, 1), 0)
            percent_payment_sum = payments_dict.get((credit_db.id, 2), 0)

            credit = schemas.CreditBaseFalse(
                issuance_date=credit_db.issuance_date,
                is_closed=False,
                return_date=credit_db.return_date,
                overdue_days=overdue_days,
                body=credit_db.body,
                percent=credit_db.percent,
                body_payment_sum=body_payment_sum,
                percent_payment_sum=percent_payment_sum,
            )

        credits.append(credit)

    return {'data': credits}


async def plans_insert_service(file: UploadFile, db: Session):
    data = await file.read()
    df = pd.read_excel(BytesIO(data), engine='xlrd')

    # duplicate validation
    duplicates = df.duplicated(subset=['category_id', 'period'], keep=False)
    if duplicates.any():
        raise HTTPException(status_code=400, detail='Duplicate category_id and period found in the file')

    data_json = df.to_json(orient='records')
    data = json.loads(data_json)

    for record in data:
        try:
            validated_record = schemas.PlansBase(**record)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=e.errors())

        existing_record = db.query(Plans).filter(
            Plans.period == validated_record.period,
            Plans.category_id == validated_record.category_id
        ).first()

        if existing_record is not None:
            raise HTTPException(status_code=400, detail='Record with this date already exists')

        new_record = Plans(**record)
        db.add(new_record)

    db.commit()

    return {'filename': file.filename, 'data': data}


def plans_performance_service(date: str, db: Session):
    validated_date = validators.date_validator(date)
    plans_db = db.query(Plans).filter(
        extract('year', Plans.period) == validated_date.year,
        extract('month', Plans.period) == validated_date.month
    ).all()
    plans = []
    for plan_db in plans_db:
        if plan_db.category_id == 3:
            credits_sum = utils.plans_sum_calculation(db, Credits.body, Credits.issuance_date, plan_db.period,
                                                      validated_date)
            plan = schemas.PlansPerformanceIssuance(
                month=plan_db.period.month,
                category=plan_db.category_id,
                sum=plan_db.sum,
                credits_sum=credits_sum,
                percentage=utils.calculate_percentage(credits_sum, plan_db.sum)
            )
        else:
            payments_sum = utils.plans_sum_calculation(db, Payments.sum, Payments.payment_date, plan_db.period,
                                                       validated_date)

            plan = schemas.PlansPerformanceCollection(
                month=plan_db.period.month,
                category=plan_db.category_id,
                sum=plan_db.sum,
                payments_sum=payments_sum,
                percentage=utils.calculate_percentage(payments_sum, plan_db.sum)
            )
        plans.append(plan)

    return {'data': plans}


def year_performance_service(year: str, db: Session):
    validated_year = validators.year_validator(year)
    plans_db = db.query(Plans).filter(
        extract('year', Plans.period) == validated_year,
    ).all()

    plans_grouped_by_date = defaultdict(list)

    for plan in plans_db:
        plans_grouped_by_date[plan.period].append(plan)

    results = []
    for date, plan in plans_grouped_by_date.items():
        credit_count, credit_sum, percentage_of_issuance = utils.get_count_sum_and_percentage(
            db, Credits, Credits.issuance_date, date, Credits.body, plan[0].sum
        )

        payment_count, payment_sum, percentage_of_payments = utils.get_count_sum_and_percentage(
            db, Payments, Payments.payment_date, date, Payments.sum, plan[1].sum
        )

        total_body = utils.calculate_total(db,  Credits.body, Credits.issuance_date, validated_year)
        total_payments = utils.calculate_total(db,  Payments.sum, Payments.payment_date, validated_year)

        percentage_of_issuance_per_year = utils.calculate_percentage(credit_sum, total_body)
        percentage_of_payments_per_year = utils.calculate_percentage(payment_sum, total_payments)

        performance = schemas.YearPerformance(
            year_and_month=date.strftime("%Y-%m"),
            amount_of_issuance=credit_count,
            issuance_plan_sum=plan[0].sum,
            issuance_sum=credit_sum,
            percentage_of_issuance=percentage_of_issuance,
            amount_of_payments=payment_count,
            payments_plan_sum=plan[1].sum,
            payments_sum=payment_sum,
            percentage_of_payments=percentage_of_payments,
            percentage_of_issuance_per_year=percentage_of_issuance_per_year,
            percentage_of_payments_per_year=percentage_of_payments_per_year
        )
        results.append(performance)

    return {'data': results}
