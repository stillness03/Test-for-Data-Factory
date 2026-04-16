from typing import List, Union, Dict
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from fastapi import HTTPException

from app.repositories.credits_repo import CreditRepository
from app.schemas.credit import ClosedCredit, OpenCredit, UserCreditBase, PlanPerformance, YearlyReportItem

class CreditService:
    def __init__(self, credit_repo: CreditRepository):
        self.credit_repo = credit_repo

    def get_user_credits_info(self, user_id: int) -> List[Union[ClosedCredit, OpenCredit]]:
        credits = self.credit_repo.get_users_credits(user_id)
        result = []

        for credit in credits:
            payments = self.credit_repo.get_payments_info(credit.id)

            total_debt = Decimal(str(credit.body)) + Decimal(str(credit.percent))
            total_paid = sum((Decimal(str(p.sum)) for p in payments), Decimal('0'))

            is_closed = (total_paid >= total_debt) and (credit.actual_return_date is not None)

            base_data = UserCreditBase(
                credit_id=credit.id,
                issuance_date=credit.issuance_date,
                is_closed=is_closed,
                body=credit.body,
                percent=credit.percent
            )


            if is_closed:
                result.append(ClosedCredit(
                    **base_data.model_dump(),
                    actual_return_date=credit.actual_return_date,
                    total_payments=total_paid
                    )
                )


            else:
                overdue_days = 0
                if credit.actual_return_date and credit.return_date:
                    delta = credit.actual_return_date - credit.return_date
                    overdue_days = max(delta.days, 0)

                body_paid = sum((Decimal(str(p.sum)) for p in payments if p.type_id == 1), Decimal('0'))
                interest_paid = sum((Decimal(str(p.sum)) for p in payments if p.type_id == 2), Decimal('0'))

                result.append(OpenCredit(
                    **base_data.model_dump(),
                    return_date=credit.return_date,
                    overdue_days=overdue_days,
                    body_payments=body_paid,
                    interest_payments=interest_paid
                    )
                )
        return result


    def get_plans_performance(self, date_str: str) -> List[PlanPerformance]:
        try:
            check_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Format must be YYYY-MM-DD")

        row_data = self.credit_repo.get_plans_performance_date(check_date)
        result = []

        for row in row_data:
            p_sum = Decimal(str(row.plan_sum))
            f_sum = Decimal(str(row.fact_sum or 0))

            performance_pct = (f_sum / p_sum * 100) if p_sum > 0 else 0

            result.append(PlanPerformance(
                month=row.period.strftime("%Y-%m"),
                category=row.category_name,
                plan_sum=p_sum,
                fact_sum=f_sum,
                performance_percentage=f"{round(float(performance_pct), 2)}%"
                )
            )

        return result

    def get_yearly_report(self, year: int) -> List[YearlyReportItem]:
        raw_data = self.credit_repo.get_yearly_report_data(year)
        if not raw_data: return []

        total_iss = sum((Decimal(str(r.issuance_sum or 0)) for r in raw_data), Decimal('0'))
        total_pay = sum((Decimal(str(r.payment_sum or 0)) for r in raw_data), Decimal('0'))

        return [
            YearlyReportItem.create(
                data={
                    "month": row.period.strftime("%Y-%m"),
                    "issuance_count": row.issuance_count or 0,
                    "issuance_sum": row.issuance_sum or 0,
                    "payment_count": row.payment_count or 0,
                    "payment_sum": row.payment_sum or 0,
                    "plan_issuance": row.plan_issuance or 0,
                    "plan_collection": row.plan_collection or 0,
                },
                total_iss=total_iss,
                total_pay=total_pay
            ) for row in raw_data
        ]
