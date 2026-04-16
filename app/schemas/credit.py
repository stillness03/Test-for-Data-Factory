from pydantic import BaseModel, ConfigDict, PlainSerializer
from datetime import date
from typing import Annotated
from decimal import Decimal, ROUND_HALF_UP

PRECISION = Decimal('0.01')

Money = Annotated[
    Decimal,
    PlainSerializer(lambda v: float(v.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)), return_type=float)
]

class CreditBaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders = {
        Decimal: lambda v: str(v.quantize(PRECISION))
        }
    )

    @classmethod
    def round_money(cls, v):
        if v is None:
            return v
        if isinstance(v, (float, str, Decimal, int)):
            return Decimal(str(v)).quantize(PRECISION, rounding=ROUND_HALF_UP)
        return v




class UserCreditBase(CreditBaseSchema):
    credit_id: int
    issuance_date: date
    is_closed: bool
    body: Money
    percent: Money


class ClosedCredit(UserCreditBase):
    is_closed: bool = True
    actual_return_date: date
    total_payments: Money


class OpenCredit(UserCreditBase):
    is_closed: bool = False
    return_date: date
    overdue_days: int
    body_payments: Money
    interest_payments: Money



class PlanPerformance(CreditBaseSchema):
    month: str
    category: str
    plan_sum: Money
    fact_sum: Money
    performance_percentage: str


class YearlyReportItem(CreditBaseSchema):
    month: str
    issuance_count: int
    issuance_sum: Money
    payment_count: int
    payment_sum: Money
    plan_issuance: Money
    plan_collection: Money
    issuance_performance: str
    collection_performance: str
    issuance_year_share: str
    payment_year_share: str

    @classmethod
    def create(cls, data: dict, total_iss: Decimal, total_pay: Decimal):
        def pct(part, whole):
            part_dec = Decimal(str(part or 0))
            whole_dec = Decimal(str(whole or 0))
            return f"{round(float(part_dec / whole_dec * 100), 2)}%" if whole_dec > 0 else "0%"

        return cls(
            **data,
            issuance_performance=pct(data["issuance_sum"], data["plan_issuance"]),
            collection_performance=pct(data["payment_sum"], data["plan_collection"]),
            issuance_year_share=pct(data["issuance_sum"], total_iss),
            payment_year_share=pct(data["payment_sum"], total_pay)
        )