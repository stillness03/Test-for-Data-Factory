from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Dictionary(Base):
    __tablename__ = 'dictionary'
    id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False)

    plans = relationship("Plans", back_populates="category")
    payments = relationship("Payments", back_populates="payment_type")