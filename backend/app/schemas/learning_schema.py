from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Any

class ConceptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: str
    category: str
    learning_content: Optional[str] = ""
    prerequisites: List[str] = []

class PrerequisiteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    concept_id: str
    prerequisite_id: str

class StudentMasteryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    concept_id: str
    concept_name: Optional[str] = None
    mastery: float
    confidence: float
    attempts_count: int
    success_count: int
    last_updated: Optional[str] = None

class TestCase(BaseModel):
    input: Any
    expected: Any

class TestCaseResult(BaseModel):
    test_num: int
    input: Any
    expected: Any
    actual: Any
    passed: bool
    stdout: Optional[str] = ""
    error: Optional[str] = None
    execution_time_ms: float = 0.0

class QuestionSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    concept_id: str
    title: str
    difficulty: str
    allowed_languages: str

class QuestionDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    concept_id: str
    concept_name: Optional[str] = None
    title: str
    description: str
    difficulty: str
    allowed_languages: str
    starter_code: str
    visible_tests: List[TestCase]

class CodeRunRequest(BaseModel):
    code: str
    language: str = "python"
    question_id: Optional[int] = None
    custom_tests: Optional[List[TestCase]] = None

class CodeRunResponse(BaseModel):
    status: str  # passed, failed, error, timeout
    stdout: str
    stderr: str
    passed_tests: int
    total_tests: int
    test_results: List[TestCaseResult]
    execution_time_ms: float

class SubmissionCreate(BaseModel):
    session_id: int
    student_id: str
    question_id: int
    code: str

class VivaQuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    submission_id: int
    question_text: str
    question_type: str
    context: Optional[str] = None

class VivaAnswerRequest(BaseModel):
    viva_question_id: int
    response_text: str

class VivaAnswerResponse(BaseModel):
    viva_question_id: int
    score: float
    feedback: str
    evaluated_at: str

class SubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    session_id: int
    student_id: str
    question_id: int
    code: str
    status: str
    passed_tests: int
    total_tests: int
    execution_output: Optional[str] = ""
    created_at: Optional[str] = None
    viva_questions: List[VivaQuestionOut] = []

class AdaptiveRecommendationOut(BaseModel):
    recommended_concept: ConceptOut
    recommended_question: QuestionDetailOut
    reason: str
    prerequisites_met: bool
    current_mastery: float

class ReviewNoteCreate(BaseModel):
    trainer_id: str = "trainer-1"
    status: str = Field(default="Needs Review")
    notes: str = Field(default="")

class ReviewNoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    session_id: int
    trainer_id: str
    status: str
    notes: str
    created_at: Optional[str] = None
