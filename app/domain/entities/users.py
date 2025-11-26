from sqlalchemy import Column, Integer, String
from app.infrastructure.db import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    userid = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    useremail = Column(String, unique=True, index=True, nullable=False)
    userpassword = Column(String, nullable=False)
    userposition = Column(String, default="Intern")
