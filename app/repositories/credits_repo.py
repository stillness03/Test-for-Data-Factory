from sqlalchemy import func, and_, select, case, extract
from sqlalchemy.orm import Session
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


    def get_yearly_performance(self, year: int):
        issuance_stats = self.db.query(
            extract('month', Credits.issuance_date).label('month'),
            func.count(Credits.id).label('count'),
            func.sum(Credits.body).label('sum')
        ).filter(extract('year', Credits.issuance_date) == year)\
        .group_by(extract('month', Credits.issuance_date)).subquery()

        payment_stats = self.db.query(
            extract('month', Payments.payment_date).label('month'),
            func.count(Payments.id).label('count'),
            func.sum(Payments.sum).label('sum')
        ).filter(extract('year', Payments.payment_date) == year) \
            .group_by(extract('month', Payments.payment_date)).subquery()

        return self.db.query(
            Plans.period,
            Plans.category_id,
            Plans.sum.label('plan_sum'),
            func.coalesce(issuance_stats.c.count, 0).label('issuance_count'),
            func.coalesce(issuance_stats.c.sum, 0).label('issuance_sum'),
            func.coalesce(payment_stats.c.count, 0).label('payment_count'),
            func.coalesce(payment_stats.c.sum, 0).label('payment_sum')
        ).outerjoin(issuance_stats, extract('month', Plans.period) == issuance_stats.c.month) \
            .outerjoin(payment_stats, extract('month', Plans.period) == payment_stats.c.month) \
            .filter(extract('year', Plans.period) == year).all()