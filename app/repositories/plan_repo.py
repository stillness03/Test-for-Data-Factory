from sqlalchemy.orm import Session
from sqlalchemy import and_

from .base import BaseRepository
from app.models.plans import Plans
from app.models.dictionary import Dictionary

class CreditPlanRepository(BaseRepository):


    def get_category_by_name(self, name: str):
        return self.db.query(Dictionary).filter(Dictionary.name.ilike(name)).first()

    def check_plan_exists(self, category_id: int, period):
        return self.db.query(Plans).filter(
            and_(
                Plans.period == period,
                Plans.category_id == category_id
            )
        ).first()

    def create_plan(self, period, amount: float, category_id: int):
        new_plan = Plans(
            period=period,
            sum=amount,
            category_id=category_id
        )
        self.db.query(new_plan)
        return new_plan
