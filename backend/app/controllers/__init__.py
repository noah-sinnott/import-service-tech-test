from .job_controller import router as job_router
from .dashboard_controller import router as dashboard_router
from .auth_controller import router as auth_router

__all__ = ['job_router', 'dashboard_router', 'auth_router']
