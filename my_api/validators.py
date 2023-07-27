from datetime import datetime

from fastapi import Depends, HTTPException, Path
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.utils import get_db
from my_api.models import Credits


def validate_user_id(db: Session = Depends(get_db), user_id: int = Path(..., ge=1)):
    max_id = db.query(func.count(Credits.id)).scalar()
    if user_id > max_id:
        raise HTTPException(status_code=400, detail="user_id is too large")
    return user_id


def date_validator(date: str):
    date_formats = ['%Y-%m-%d', '%Y.%m.%d', '%d.%m.%Y', '%d-%m-%Y']
    for format in date_formats:
        try:
            date_object = datetime.strptime(date, format).date()
            return date_object
        except ValueError:
            pass  # go to next format
    else:
        raise HTTPException(status_code=400,
                            detail="Invalid date format, it should be YYYY-MM-DD, YYYY.MM.DD, DD.MM.YYYY or DD-MM-YYYY")


def year_validator(year: str):
    if len(year) != 4 or not year.isdigit():
        raise HTTPException(status_code=400,
                            detail="Invalid year format, it should be YYYY")
    return year
