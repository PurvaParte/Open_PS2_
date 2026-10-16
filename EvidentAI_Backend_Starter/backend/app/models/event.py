from sqlalchemy import Column, Integer, String, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from app.database.database import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(Integer, nullable=False, index=True)
    event_type = Column(String(40), nullable=False, index=True)
    data = Column(Text, nullable=False, default="")
    session = relationship("Session", back_populates="events")
    __table_args__ = (Index("ix_events_session_timestamp", "session_id", "timestamp"),)
