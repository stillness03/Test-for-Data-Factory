from sqlalchemy import Column, Float, Numeric, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Credits(Base):
    __tablename__ = 'credits'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    issuance_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=False)
    actual_return_date = Column(Date, nullable=True)
    body = Column(Numeric(precision=10, scale=2), nullable=False)
    percent = Column(Float, nullable=False)

    user = relationship("Users", back_populates="credits")
    payments = relationship("Payments", back_populates="credit")