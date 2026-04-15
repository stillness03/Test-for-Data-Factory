from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, nullable=False, unique=True)
    registration_date = Column(Date, nullable=False)

    credits = relationship("Credits", back_populates="user")