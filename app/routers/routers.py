from fastapi import APIRouter, Depends, UploadFile, File
from typing import List, Union

from app.service.credit_service import CreditService
from app.service.plan_service import PlanService
from app.core.dependencies import get_credit_service, get_plan_service
from app.schemas.credit import ClosedCredit, OpenCredit


router = APIRouter()


@router.get("/user_credits/{user_id}", response_model=List[Union[ClosedCredit, OpenCredit]])
def get_user_credits(
        user_id: int,
        credit_service: CreditService = Depends(get_credit_service),
):
    return credit_service.get_user_credits_info(user_id)


@router.post("/plans_insert")
async def upload_plans(
        file: UploadFile = File(...),
        plan_service: PlanService = Depends(get_plan_service),
):
    return plan_service.import_plans_from_excel(file)

@router.get("/plans_performance")
def get_performance(
        date: str,
        credit_service: CreditService = Depends(get_credit_service)
):
    return credit_service.get_plans_performance(date)

@router.get("/yearly_performance/{year}")
def get_yearly_performance(
    year: int,
    credit_service: CreditService = Depends(get_credit_service)
):
    return credit_service.get_yearly_report(year)