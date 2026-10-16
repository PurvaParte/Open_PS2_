from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.database import Base

class IntegritySignal(Base):
    __tablename__ = "integrity_signals"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_name = Column(String(80), nullable=False)
    severity = Column(String(20), nullable=False, default="medium")
    event_id = Column(Integer, nullable=True)
    timestamp = Column(Integer, nullable=True)
    reason = Column(Text, nullable=False)
    session = relationship("Session", back_populates="signals")
