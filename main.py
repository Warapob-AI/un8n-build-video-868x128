from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import base64

from multi_image.generate_video_base64 import generate_multi_images_video_base64

from center.generate_background_video_base64 import generate_background_video_base64
from center.generate_text import generate_text_center 

from left.generate_background_base64 import process_video_set_left_background 
from left.generate_text import generate_text_left

from right.generate_background_base64 import process_video_set_right_background 
from right.generate_text import generate_text_right

app = FastAPI()

class BackgroundVideoRequest(BaseModel):
    video_base64: str
    opacity: float 

class TextVideoRequest(BaseModel):
    text: str
    font_bin: str
    video_base64: str
    color: str
    width: int 
    height: int

class BackgroundVideoLeftRightRequest(BaseModel):
    video_base64: str
    background_color_hex: str
    
class VideoMultiImagesRequest(BaseModel):
    array_image_base64: list[str]
    width: int
    height: int
    duration: float
    fps: int
    count: int

@app.get("/", include_in_schema=False)
def index():
    return {"message": "Hello from FastAPI!"}

@app.post("/generate-multi-images-video-base64/")
async def create_multi_images_video_base64(req: VideoMultiImagesRequest):
    # แปลง base64 image list -> binary list
    images_bytes_list = [
        base64.b64decode(b64_string)  # decode base64 ล้วน ๆ เลย
        for b64_string in req.array_image_base64
    ]

    video_b64 = generate_multi_images_video_base64(
        images_bytes_list,
        width=req.width,
        height=req.height,
        duration=req.duration,
        fps=req.fps,
        count=req.count
    )
    return JSONResponse(content={"video_base64": video_b64})

@app.post("/generate-background-video-base64/")
async def create_background_video_base64(req: BackgroundVideoRequest):
    video_binary = base64.b64decode(req.video_base64.split(",")[-1])
    out_b64 = generate_background_video_base64(video_binary, req.opacity)
    return JSONResponse(content={"video_base64": out_b64})

@app.post("/generate-text-center/")
async def create_combine_video_base64(req: TextVideoRequest):
    video_data = req.video_base64
    if video_data.startswith("data:video"):
        video_data = video_data.split(",")[-1]
    video_bytes = base64.b64decode(video_data)
    # ✨ ส่ง video_bytes ตรง ๆ
    final_video_bytes = generate_text_center(req.text, req.font_bin, video_bytes, req.color, req.width, req.height)
    # ✨ Encode base64 และส่งกลับ
    video_b64 = base64.b64encode(final_video_bytes).decode('utf-8')
    return JSONResponse(content={"video_base64": video_b64})

@app.post("/generate-background-left-base64/")
async def generate_background_left_base64(req: BackgroundVideoLeftRightRequest):
    video_binary = base64.b64decode(req.video_base64.split(",")[-1])
    video_bytes = process_video_set_left_background(video_binary, req.background_color_hex)
    video_b64 = base64.b64encode(video_bytes).decode("utf-8")
    return JSONResponse(content={"video_base64": video_b64})

@app.post("/generate-text-left/")
async def create_combine_video_base64(req: TextVideoRequest):
    video_data = req.video_base64
    if video_data.startswith("data:video"):
        video_data = video_data.split(",")[-1]
    video_bytes = base64.b64decode(video_data)
    # ✨ ส่ง video_bytes ตรง ๆ
    final_video_bytes = generate_text_left(req.text, req.font_bin, video_bytes, req.color, req.width, req.height)
    # ✨ Encode base64 และส่งกลับ
    video_b64 = base64.b64encode(final_video_bytes).decode('utf-8')
    return JSONResponse(content={"video_base64": video_b64})

@app.post("/generate-background-right-base64/")
async def generate_background_right_base64(req: BackgroundVideoLeftRightRequest):
    video_binary = base64.b64decode(req.video_base64.split(",")[-1])
    video_bytes = process_video_set_right_background(video_binary, req.background_color_hex)
    video_b64 = base64.b64encode(video_bytes).decode("utf-8")
    return JSONResponse(content={"video_base64": video_b64})

@app.post("/generate-text-right/")
async def create_combine_video_base64(req: TextVideoRequest):
    video_data = req.video_base64
    if video_data.startswith("data:video"):
        video_data = video_data.split(",")[-1]
    video_bytes = base64.b64decode(video_data)
    # ✨ ส่ง video_bytes ตรง ๆ
    final_video_bytes = generate_text_right(req.text, req.font_bin, video_bytes, req.color, req.width, req.height)
    # ✨ Encode base64 และส่งกลับ
    video_b64 = base64.b64encode(final_video_bytes).decode('utf-8')
    return JSONResponse(content={"video_base64": video_b64})

