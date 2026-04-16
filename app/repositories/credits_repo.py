from sqlalchemy import func, and_, select, case, extract
from .base import BaseRepository
from app.models.credits import Credits
from app.models.payments import Payments
from app.models.dictionary import Dictionary
from app.models.plans import Plans


class CreditRepository(BaseRepository):
    def get_users_credits(self, user_id: int) -> Credits | None:
        return (self.db.query(Credits)
                .filter(Credits.user_id == user_id)
                .order_by(Credits.issuance_date.desc())
                .all()
                )

    def get_payments_info(self, credit_id: int) -> list[Payments]:
        return (
            self.db.query(Payments)
            .filter(Payments.credit_id == credit_id)
            .all()
        )


    def get_payment_types(self) -> list[Dictionary]:
        return self.db.query(Dictionary).all()


    def get_plans_performance_date(self, check_date):
        start_of_month = check_date.replace(day=1)

        issuance_fact = select(func.coalesce(func.sum(Credits.body), 0)).where(
            and_(
                Credits.issuance_date >= start_of_month,
                Credits.issuance_date <= check_date
            )
        ).scalar_subquery()

        payments_fact = select(func.coalesce(func.sum(Payments.sum), 0)).where(
            and_(
                Payments.payment_date >= start_of_month,
                Payments.payment_date <= check_date
            )
        ).scalar_subquery()

        return self.db.query(
            Plans.period,
            Dictionary.name.label("category_name"),
            Plans.sum.label("plan_sum"),
            case(
                (Dictionary.id == 3, issuance_fact),
                (Dictionary.id == 4, payments_fact),
                else_=0
            ).label("fact_sum")
        ).join(Dictionary, Plans.category_id == Dictionary.id) \
            .filter(Plans.period == start_of_month).all()

    def get_yearly_report_data(self, year: int):
        iss_sub = self.db.query(
            extract('month', Credits.issuance_date).label('month'),
            func.count(Credits.id).label('iss_count'),
            func.sum(Credits.body).label('iss_sum')
        ).filter(extract('year', Credits.issuance_date) == year) \
            .group_by(extract('month', Credits.issuance_date)).subquery()

        pay_sub = self.db.query(
            extract('month', Payments.payment_date).label('month'),
            func.count(Payments.id).label('pay_count'),
            func.sum(Payments.sum).label('pay_sum')
        ).filter(extract('year', Payments.payment_date) == year) \
            .group_by(extract('month', Payments.payment_date)).subquery()

        return self.db.query(
            Plans.period,
            func.max(iss_sub.c.iss_count).label('issuance_count'),
            func.max(iss_sub.c.iss_sum).label('issuance_sum'),
            func.sum(case((Plans.category_id == 3, Plans.sum), else_=0)).label('plan_issuance'),
            func.max(pay_sub.c.pay_count).label('payment_count'),
            func.max(pay_sub.c.pay_sum).label('payment_sum'),
            func.sum(case((Plans.category_id == 4, Plans.sum), else_=0)).label('plan_collection')
        ).outerjoin(iss_sub, extract('month', Plans.period) == iss_sub.c.month) \
            .outerjoin(pay_sub, extract('month', Plans.period) == pay_sub.c.month) \
            .filter(extract('year', Plans.period) == year) \
            .group_by(Plans.period) \
            .order_by(Plans.period).all()