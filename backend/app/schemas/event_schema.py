from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Literal, Any

EventType = Literal[
    "insert",
    "delete",
    "paste",
    "run",
    "focus",
    "blur",
    "focus_change",
    "tab_visibility",
    "submit",
    "other"
]

class EventCreate(BaseModel):
    session_id: int = Field(gt=0)
    timestamp: int = Field(ge=0, description="Client relative elapsed timestamp in milliseconds")
    event_type: EventType
    data: str = Field(default="", max_length=1_000_000)

    @field_validator("data", mode="before")
    @classmethod
    def normalize_data(cls, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, (dict, list)):
            import json
            return json.dumps(value, ensure_ascii=False)
        return str(value)

class SessionCreate(BaseModel):
    student_id: str = Field(min_length=1, max_length=128)

class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: str
    started_at: str | None = None
    ended_at: str | None = None

class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    session_id: int
    timestamp: int
    event_type: str
    data: str

class IntegritySignalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = None
    session_id: int
    rule_name: str
    severity: str
    event_id: int | None = None
    timestamp: int | None = None
    reason: str
    review_guidance: str | None = None
