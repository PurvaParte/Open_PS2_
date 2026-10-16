from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.database import Base

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(128), nullable=False, index=True)
    started_at = Column(String(40), nullable=True)
    ended_at = Column(String(40), nullable=True)

    events = relationship("Event", back_populates="session", cascade="all, delete-orphan", order_by="Event.timestamp")
    signals = relationship("IntegritySignal", back_populates="session", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="session", cascade="all, delete-orphan")
    review_notes = relationship("ReviewNote", back_populates="session", cascade="all, delete-orphan")
