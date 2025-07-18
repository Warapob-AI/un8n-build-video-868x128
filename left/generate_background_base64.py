import os
import tempfile
import numpy as np
from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip

def hex_to_rgb(hex_color: str):
    """Converts a hex color string to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def process_video_set_left_background(video_bytes: bytes, background_color_hex: str) -> bytes:
    """
    รับวิดีโอ (bytes) แล้วนำพื้นหลังสีทึบไปวางทับทางด้านซ้ายของวิดีโอ
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        temp_video_file.write(video_bytes)
        temp_video_path = temp_video_file.name

    output_path = temp_video_path.replace(".mp4", "_output.mp4")
    
    # ประกาศตัวแปรไว้นอก try เพื่อให้ finally มองเห็น
    base_clip = None
    final_clip = None

    try:
        base_clip = VideoFileClip(temp_video_path)
        width, height = base_clip.size
        half_width = width // 2
        left_width = half_width 

        rgb_color = hex_to_rgb(background_color_hex)

        left_overlay = ColorClip(
            size=(left_width, height),
            color=rgb_color,
            duration=base_clip.duration
        ).set_position((0, 0))

        final_clip = CompositeVideoClip([base_clip, left_overlay])

        final_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            audio=True,  # ❗ ไม่มีเสียงเลย
            preset='ultrafast',  # หรือ ultrafast ถ้าอยากเร็ว
            ffmpeg_params=["-movflags", "+faststart"],
            verbose=False,
            logger=None
        )

        with open(output_path, "rb") as f:
            output_video_bytes = f.read()

        return output_video_bytes

    finally:
        # --- จุดที่แก้ไข: ปิดการใช้งานคลิปทั้งหมดก่อนลบไฟล์ ---
        # ต้องแน่ใจว่าอ็อบเจกต์ถูกสร้างแล้วก่อนที่จะพยายามปิด
        if base_clip:
            base_clip.close()
        if final_clip:
            final_clip.close()

        # ลบไฟล์ชั่วคราวหลังจากปิด handle เรียบร้อยแล้ว
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        if os.path.exists(output_path):
            os.remove(output_path)