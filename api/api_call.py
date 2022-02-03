from fastapi import APIRouter
from api.endpoints.detectface import router as detect_router
#from api.api_call import router as api_router

router = APIRouter()
router.include_router(detect_router)