from datetime import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean


from app.database import Base

metadata = Base.metadata


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)
    last_activity_at = Column(TIMESTAMP, default=datetime.utcnow)
    balance = Column(Integer, default=0)
    disabled = Column(Boolean, default=False)
