from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import numpy as np
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import tempfile, os
from PIL import ImageColor

def generate_text_left(text, font_bin, video_bytes, text_color, canvas_width, canvas_height):
    if (text_color is None): 
        text_color = "#222222"
        
    font_bytes = BytesIO(base64.b64decode(font_bin))
    
    margin = 25
    max_text_width = (canvas_width // 2) - (margin * 2)
    
    def wrap_text(text, font, draw_context, max_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            line_bbox = draw_context.textbbox((0, 0), test_line, font=font)
            line_width = line_bbox[2] - line_bbox[0]
            if line_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines
    
    font_size = 50
    min_font_size = 15

    resolved_color = (255, 255, 255)
    try:
        resolved_color = ImageColor.getrgb(text_color)
    except ValueError:
        pass
        
    # ลูปลดขนาดฟอนต์จนข้อความไม่เกินพื้นที่
    while font_size >= min_font_size:
        font_bytes.seek(0)
        font = ImageFont.truetype(font_bytes, size=font_size)
        image = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        lines = wrap_text(text, font, draw, max_text_width)
        
        # 1. คำนวณขนาดข้อความรวมทั้งหมด
        line_spacing = 18 if len(lines) > 1 else 0
        line_heights = []
        line_bboxes = []

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            height = bbox[3] - bbox[1]
            line_heights.append(height)
            line_bboxes.append(bbox)

        total_text_height = sum(line_heights) + (len(lines) - 1) * line_spacing

        print("T : ", total_text_height ,"********************************")
        print("C : ", canvas_height ,"********************************")

        # 2. คำนวณ y จุดเริ่มต้นให้อยู่กึ่งกลางพอดี
        current_y = (canvas_height - total_text_height) // 2
        
        if total_text_height <= (canvas_height - margin * 2):
            break
        font_size -= 1
    
    # สร้าง Canvas ใหม่อีกครั้ง (เผื่อฟอนต์เปลี่ยน)
    font_bytes.seek(0)
    font = ImageFont.truetype(font_bytes, size=font_size)
    image = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    current_y = ((canvas_height - total_text_height) // 2)
    margin = margin + 3

    print(canvas_height, total_text_height, current_y,  "***********")
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        vertical_offset = bbox[1]  # นี่คือค่าที่ต้องหักออกเพื่อชดเชย baseline

        x = margin
        y = current_y - vertical_offset  # หักออกเพื่อเริ่มวาดจากขอบบนของตัวอักษรจริง ๆ

        print(current_y, vertical_offset)
        draw.text((x, y), line, font=font, fill=resolved_color)

        current_y += line_height + line_spacing

    text_image_np = np.array(image)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        temp_video_file.write(video_bytes)
        video_path = temp_video_file.name

    clip = VideoFileClip(video_path)

    text_clip = (
        ImageClip(text_image_np, ismask=False)  # ยืนยันว่าไม่ใช่ mask
        .set_duration(clip.duration)
        .set_position((0, "center"))).crossfadein(0.5)
    


    final = CompositeVideoClip([clip, text_clip])

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as output_file:
        output_path = output_file.name
    final.write_videofile(
        output_path,
            codec="libx264",
            audio_codec="aac",
            audio=True,  # ❗ ไม่มีเสียงเลย
            preset='ultrafast',  # หรือ ultrafast ถ้าอยากเร็ว
            ffmpeg_params=["-movflags", "+faststart"],
            verbose=False,
            logger=None
        )
    
    # ปิด clip และ final เพื่อปลดล็อกไฟล์
    final.close()
    clip.close()

    with open(output_path, "rb") as f:
        final_video_bytes = f.read()

    os.remove(video_path)
    os.remove(output_path)

    return final_video_bytes