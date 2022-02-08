from fastapi import APIRouter, File, UploadFile
from PIL import Image
from io import BytesIO
import numpy as np
import torch
from core.models.output import MessageOutput
from core.models.input import MessageInput

from core.logic.yolov5face.detectface import detect_one_trt
router = APIRouter()


@router.post("/hello", )#response_model=MessageOutput, tags=["hello post"])
def hello_endpoint(im: UploadFile):

    extension = im.filename.split(".")[-1] in ("jpg", "jpeg", "png")
    if not extension:
        return "Image must be jpg or png format!"
    else:
        print("You have inserted the righttttttttttttttt extension")

    
    image = Image.open(BytesIO(im.file.read()))

    print(np.array(image).shape)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("the device being used by torch is ====================", device)

    return detect_one_trt(np.array(image), device)

    # {
    #     "message1": "Hello, world!",
    #     "message2": f"The largest prime factor of {n} is {largest_prime_factor}. Calculation took {elapsed_time:0.3f} seconds.",
    #     "n": n,
    #     "largest_prime_factor": largest_prime_factor,
    #     "elapsed_time": elapsed_time,
    # }