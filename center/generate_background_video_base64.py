import numpy as np
from PIL import Image
import base64
from io import BytesIO
import tempfile
import os
from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip

def generate_background_video_base64(video_binary, opacity_percent):
    opacity = opacity_percent / 100

    temp_path = None
    output_path = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video_file:
            temp_path = temp_video_file.name
            temp_video_file.write(video_binary)
            temp_video_file.flush()

        clip = VideoFileClip(temp_path)
        black_overlay = ColorClip(size=clip.size, color=(0, 0, 0), duration=clip.duration)
        black_overlay = black_overlay.set_opacity(opacity)
        final = CompositeVideoClip([clip, black_overlay])

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as out_file:
            output_path = out_file.name
            print(output_path)
            final.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="libmp3lame",
                audio=True,  # ❗ ไม่มีเสียงเลย
                preset='ultrafast',  # หรือ ultrafast ถ้าอยากเร็ว
                ffmpeg_params=["-movflags", "+faststart"],
                verbose=False,
                logger=None
            )
        with open(output_path, "rb") as f:
            result_b64 = base64.b64encode(f.read()).decode("utf-8")

    finally:
        # ปิดคลิปและลบไฟล์ชั่วคราว
        if 'clip' in locals():
            clip.close()
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        if output_path and os.path.exists(output_path):
            os.remove(output_path)

    return result_b64


