from fastapi import Depends
from sqlalchemy.orm import Session

from app.repositories.plan_repo import CreditPlanRepository
from app.service.credit_service import CreditService
from app.service.plan_service import PlanService
from app.repositories.credits_repo import CreditRepository

from app.core.database import get_db

def get_credit_repository(db: Session = Depends(get_db)):
    return CreditRepository(db)

def get_plan_repository(db: Session = Depends(get_db)):
    return CreditPlanRepository(db)

def get_credit_service(
    credit_repo: CreditRepository = Depends(get_credit_repository)
):
    return CreditService(credit_repo)

def get_plan_service(plan_repo: CreditPlanRepository = Depends(get_plan_repository)):
     return PlanService(plan_repo)