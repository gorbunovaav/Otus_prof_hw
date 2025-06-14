from fastapi import APIRouter
from .jwt_auth import router

# auth_router.include_router(jwt_auth_router)

# router = APIRouter()
# router.include_router(router=auth_router)