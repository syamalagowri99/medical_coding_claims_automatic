from fastapi import APIRouter
from app.api import auth, documents, patients, claims, mcp
from app.core.config import settings

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(claims.router, prefix="/claims", tags=["claims"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])

# Conditionally include development-only routes
if settings.ENABLE_DEV_ENDPOINTS:
    try:
        from app.api import dev
        api_router.include_router(dev.router, prefix='/dev', tags=['dev'])
    except ImportError:
        pass
