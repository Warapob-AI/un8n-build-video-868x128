import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import tempfile
import os

def generate_text_center(text, font_bin, video_bytes, color, canvas_width, canvas_height):
    font_bytes = BytesIO(base64.b64decode(font_bin))
    font = ImageFont.truetype(font_bytes, size=70)

    # ====== สร้างข้อความเป็นภาพ (text image) ======
    margin = 20
    image = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            w, _ = draw.textbbox((0, 0), test_line, font=font)[2:]
            if w + margin * 2 <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    lines = wrap_text(text, font, canvas_width)
    # วัด bbox ของแต่ละบรรทัดเพื่อใช้หาความสูงรวมของข้อความทั้งหมด
    line_bboxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    line_heights = [bbox[3] - bbox[1] for bbox in line_bboxes]

    line_spacing = 18 if len(lines) > 1 else 0
    total_text_height = sum(line_heights) + (len(lines) - 1) * line_spacing

    # คำนวณตำแหน่ง y เริ่มต้น ให้อยู่กึ่งกลาง canvas
    start_y = (canvas_height - total_text_height) // 2

    current_y = start_y
    shadow_offset = (2, 2)  # ระยะเงา
    shadow_color = "black"  # สีของเงา

    for i, (line, bbox) in enumerate(zip(lines, line_bboxes)):
        line_width = bbox[2] - bbox[0]
        vertical_offset = bbox[1]
        x = (canvas_width - line_width) // 2
        y = current_y - vertical_offset

        # ✨ วาด shadow ก่อน
        draw.text((x + shadow_offset[0], y + shadow_offset[1]), line, font=font, fill=shadow_color)

        # ✨ วาดข้อความจริง
        draw.text((x, y), line, font=font, fill=color)  # ใช้ `color` ที่รับเข้ามาแทน fill="white"

        current_y += line_heights[i] + line_spacing

    text_image_np = np.array(image)

    # ====== Save video to temp file ======
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        temp_video_file.write(video_bytes)
        video_path = temp_video_file.name

    # ====== Load video and overlay text ======
    clip = VideoFileClip(video_path)
    text_clip = ImageClip(text_image_np).set_duration(clip.duration).set_position(("center", "center"))

    final = CompositeVideoClip([clip, text_clip])

    # ====== Write final video ======
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as output_file:
        output_path = output_file.name
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
    clip.close()  # ❗❗ สำคัญมาก
    final.close()

    with open(output_path, "rb") as f:
        final_video_bytes = f.read()

    os.remove(video_path)
    os.remove(output_path)

    return final_video_bytes