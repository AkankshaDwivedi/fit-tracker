from database_engine import Base
from datetime import date, datetime
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, Date



class UserData(Base):
    __tablename__ = "user_fit_data"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True)
    steps = Column(Integer,index=True)
    heart_beat = Column(Integer,index=True)
    met = Column(Float,index=True)
    height = Column(Integer,index=True)
    weight = Column(Integer,index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class UserDailySummary(Base):
    __tablename__ = "user_daily_summary"
    user_id = Column(String(255), ForeignKey("user_fit_data.user_id"), primary_key=True, index=True)
    total_steps = Column(Integer,index=True)
    distance = Column(Float,index=True)
    average_heart_beat = Column(Float,index=True)
    kcal_burned = Column(Float,index=True)
    date = Column(Date, primary_key=True, default=datetime.utcnow().date) 


class UserResponse(BaseModel):
    user_id: str
    steps: int
    heart_beat: int
    met: float
    height: int
    weight: int


class UserDailySummaryResponse(BaseModel):
    user_id: str
    total_steps: int
    distance: float
    average_heart_beat: float   
    kcal_burned: float
    date: date