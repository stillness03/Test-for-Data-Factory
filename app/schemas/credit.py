from pydantic import BaseModel, field_validator
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

PRECISION = Decimal('0.01')


class CreditBaseSchema(BaseModel):
    @field_validator(
        'body', 'percent', 'total_payments',
        'body_payments', 'interest_payments',
        'issuance_sum', 'payment_sum', 'plan_issuance', 'plan_collection',
        'fact_sum', 'plan_sum',
        mode='before', check_fields=False
    )
    @classmethod
    def round_money(cls, v):
        if v is None:
            return Decimal('0.00')
        if isinstance(v, (float, str, Decimal, int)):
            return Decimal(str(v)).quantize(PRECISION, rounding=ROUND_HALF_UP)
        return v

    class Config:
        from_attributes = True


class UserCreditBase(CreditBaseSchema):
    credit_id: int
    issuance_date: date
    is_closed: bool
    body: Decimal
    percent: Decimal


class ClosedCredit(UserCreditBase):
    is_closed: bool = True
    actual_return_date: date
    total_payments: Decimal


class OpenCredit(UserCreditBase):
    is_closed: bool = False
    return_date: date
    overdue_days: int
    body_payments: Decimal
    interest_payments: Decimal



class PlanPerformance(CreditBaseSchema):
    month: str
    category: str
    plan_sum: Decimal
    fact_sum: Decimal
    performance_percentage: str


class YearlyReportItem(CreditBaseSchema):
    month: str
    issuance_count: int
    issuance_sum: Decimal
    payment_count: int
    payment_sum: Decimal
    plan_issuance: Decimal
    plan_collection: Decimal
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