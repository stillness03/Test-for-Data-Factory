from sqlalchemy import Column, Integer, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Payments(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    sum = Column(Numeric(precision=15, scale=2), nullable=False)
    payment_date = Column(Date, nullable=False)
    credit_id = Column(Integer, ForeignKey('credits.id'), nullable=False)
    type_id = Column(Integer, ForeignKey('dictionary.id'), nullable=False)

    credit = relationship("Credits", back_populates="payments")
    payment_type = relationship("Dictionary")