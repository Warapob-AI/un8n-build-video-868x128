import os
import tempfile
import numpy as np
from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip

def hex_to_rgb(hex_color: str):
    """Converts a hex color string to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def process_video_set_right_background(video_bytes: bytes, background_color_hex: str) -> bytes:
    """
    รับวิดีโอ (bytes) แล้วนำพื้นหลังสีทึบไปวางทับทางด้านขวาของวิดีโอ
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        temp_video_file.write(video_bytes)
        temp_video_path = temp_video_file.name

    output_path = temp_video_path.replace(".mp4", "_output.mp4")
    
    base_clip = None
    final_clip = None

    try:
        base_clip = VideoFileClip(temp_video_path)
        width, height = base_clip.size
        half_width = width // 2
        right_width = width - half_width  # จะแก้ปัญหา width คี่

        rgb_color = hex_to_rgb(background_color_hex)
        # เปลี่ยนตำแหน่งจาก (0, 0) เป็น (half_width, 0) เพื่อวางที่ขวา
        right_overlay = ColorClip(
            size=(right_width, height),
            color=rgb_color,
            duration=base_clip.duration
        ).set_position((half_width, 0))

        final_clip = CompositeVideoClip([base_clip, right_overlay])

        final_clip.write_videofile(
            output_path,
            codec="libx264",                # ✅ ใช้ H.264 ที่รองรับดีสุด
            audio_codec="aac",              # ✅ ใช้เสียง AAC ซึ่ง WMP รองรับ
            audio=True,                     # ✅ ใส่ audio track
            preset='slow',
            ffmpeg_params=[
                "-movflags", "+faststart",
                "-b:v", "2500k"  # ลอง bitrate 2.5Mbps เพื่อให้ภาพคมชัดขึ้น
            ],
            verbose=False,
            logger=None
        )
        with open(output_path, "rb") as f:
            output_video_bytes = f.read()

        return output_video_bytes

    finally:
        if base_clip:
            base_clip.close()
        if final_clip:
            final_clip.close()

        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        if os.path.exists(output_path):
            os.remove(output_path)
