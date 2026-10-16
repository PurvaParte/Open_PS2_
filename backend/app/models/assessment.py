from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(128), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(Text, nullable=False)
    status = Column(String(30), nullable=False, default="pending")
    passed_tests = Column(Integer, nullable=False, default=0)
    total_tests = Column(Integer, nullable=False, default=0)
    execution_output = Column(Text, nullable=True, default="")
    created_at = Column(String(40), nullable=True)

    session = relationship("Session", back_populates="submissions")
    question = relationship("Question", back_populates="submissions")
    viva_questions = relationship("VivaQuestion", back_populates="submission", cascade="all, delete-orphan")

class VivaQuestion(Base):
    __tablename__ = "viva_questions"
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(40), nullable=False, default="rationale")
    context = Column(Text, nullable=True, default="")

    submission = relationship("Submission", back_populates="viva_questions")
    responses = relationship("VivaResponse", back_populates="viva_question", cascade="all, delete-orphan")

class VivaResponse(Base):
    __tablename__ = "viva_responses"
    id = Column(Integer, primary_key=True, index=True)
    viva_question_id = Column(Integer, ForeignKey("viva_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    response_text = Column(Text, nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    feedback = Column(Text, nullable=False, default="")
    evaluated_at = Column(String(40), nullable=True)

    viva_question = relationship("VivaQuestion", back_populates="responses")

class ReviewNote(Base):
    __tablename__ = "review_notes"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    trainer_id = Column(String(128), nullable=False, default="trainer-1")
    status = Column(String(40), nullable=False, default="Needs Review")
    notes = Column(Text, nullable=False, default="")
    created_at = Column(String(40), nullable=True)

    session = relationship("Session", back_populates="review_notes")
