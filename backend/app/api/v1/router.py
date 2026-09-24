from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.rfqs import router as rfqs_router
from app.api.v1.auctions import router as auctions_router
from app.api.v1.bids import router as bids_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(rfqs_router)
api_router.include_router(auctions_router)
api_router.include_router(bids_router)
