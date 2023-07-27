
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from core.utils import get_db
from . import service
from . import schemas
from .validators import validate_user_id

router = APIRouter()


@router.get('/user_credits/{user_id}', response_model=schemas.CreditResponse)
def get_credits(user_id: int = Depends(validate_user_id), db: Session = Depends(get_db)):
    return service.get_credits_service(user_id, db)


@router.post('/plans_insert')
async def plans_insert(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await service.plans_insert_service(file, db)


@router.get('/plans_performance', response_model=schemas.PlansPerformanceResponse)
def plans_performance(date, db: Session = Depends(get_db)):
    return service.plans_performance_service(date, db)


@router.get('/year_performance', response_model=schemas.YearPerformanceResponse)
def year_performance(year, db: Session = Depends(get_db)):
    return service.year_performance_service(year, db)
