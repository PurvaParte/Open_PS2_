from .sessions import router as sessions_router
from .learning import router as learning_router
from .assessment import router as assessment_router
from .trainer import router as trainer_router

__all__ = ["sessions_router", "learning_router", "assessment_router", "trainer_router"]
