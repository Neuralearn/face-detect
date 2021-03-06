from core.config import API, PROJECT_NAME
from fastapi import FastAPI

from api.endpoints.detectface import router as detect_router
from api.api_call import router as api_router


from core.logic.yolov5face.models.trt_model import TrtModel

app = FastAPI(
    title=PROJECT_NAME,
    # if not custom domain
    # openapi_prefix="/prod"
)

app.include_router(api_router, prefix=API)

model_trt=TrtModel("core/logic/yolov5face/weights/yolov5n-face.trt")

@app.get("/ping", summary="Check that the service is operational")
def pong():
    
    
    return {"ping": "pong!"}