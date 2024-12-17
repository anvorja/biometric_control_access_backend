from fastapi import APIRouter
from app.api.v1.endpoints import auth, access, biometric

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(access.router, prefix="/access", tags=["access-control"])
api_router.include_router(biometric.router, prefix="/biometric", tags=["biometric"])

