from sqlalchemy import Column, Integer, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Plans(Base):
    __tablename__ = 'plans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    period = Column(Date, nullable=False)
    sum = Column(Numeric(precision=15, scale=2), nullable=False)
    category_id = Column(Integer, ForeignKey('dictionary.id'), nullable=False)

    category = relationship("Dictionary", back_populates="plans")
