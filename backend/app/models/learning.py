from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.database import Base

class Concept(Base):
    __tablename__ = "concepts"
    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=False, default="")
    category = Column(String(64), nullable=False, default="Core")
    learning_content = Column(Text, nullable=True, default="")

    questions = relationship("Question", back_populates="concept")
    masteries = relationship("StudentMastery", back_populates="concept")

class Prerequisite(Base):
    __tablename__ = "prerequisites"
    id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(String(64), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    prerequisite_id = Column(String(64), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("concept_id", "prerequisite_id", name="uq_concept_prerequisite"),)

class StudentMastery(Base):
    __tablename__ = "student_mastery"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(128), nullable=False, index=True)
    concept_id = Column(String(64), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    mastery = Column(Float, nullable=False, default=0.2)
    confidence = Column(Float, nullable=False, default=0.5)
    attempts_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    last_updated = Column(String(40), nullable=True)

    concept = relationship("Concept", back_populates="masteries")
    __table_args__ = (UniqueConstraint("student_id", "concept_id", name="uq_student_concept"),)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(String(64), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(20), nullable=False, default="medium")
    allowed_languages = Column(String(64), nullable=False, default="python")
    starter_code = Column(Text, nullable=False, default="")
    visible_tests = Column(Text, nullable=False, default="[]")
    hidden_tests = Column(Text, nullable=False, default="[]")

    concept = relationship("Concept", back_populates="questions")
    submissions = relationship("Submission", back_populates="question")
