import math
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from moviepy.editor import VideoClip, concatenate_videoclips
import tempfile, base64, os

def generate_multi_images_video_base64(images_bytes_list, width, height, duration, fps, count):
    num_images = len(images_bytes_list)
    fade_duration = 2

    # คำนวณ per_clip_duration ใหม่:

    if (num_images == 1): 
        per_clip_duration = (duration)

    elif (num_images == 2): 
        per_clip_duration = ((duration + (num_images - 1) * fade_duration) / num_images) + 1

    else: 
        per_clip_duration = ((duration + (num_images - 1) * fade_duration) / num_images) + fade_duration

    clips = []
    
    for idx, image_bytes in enumerate(images_bytes_list):
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        full_img = np.array(image)

        # 1. เริ่มจากข้างบนขวาสุด และค่อย ๆ เลื่อนลงเอียงซ้าย 
        def make_frame_1(t):
            progress = t / per_clip_duration  # ค่า 0 → 1

            h, w, _ = full_img.shape
            max_dx = w - width

            # ✅ แนวนอน: เริ่มจากขวาสุด แล้วค่อย ๆ เลื่อนซ้าย
            dx = round((1 - progress) * max_dx)

            # ✅ แนวตั้ง: เริ่มจาก "บน-กลาง" (30%) → ล่างลึกขึ้น (80%)
            dy_start = int((h - height) * 0.3)
            dy_end   = int((h - height) * 0.6)
            dy = round(dy_start + progress * (dy_end - dy_start))

            frame = full_img[dy:dy + height, dx:dx + width]
            return frame

        # 2.เลื่อนจากซ้ายไปขวา (Slow Pan Right)
        def make_frame_2(t):
            progress = t / per_clip_duration
            h, w, _ = full_img.shape
            max_dx = w - width
            max_dy = h - height

            dx = round(progress * max_dx * 1.0)
            dy = round(progress * max_dy * 0.15)  # ขยับลงด้านล่าง 10% ของระยะที่เหลือ

            frame = full_img[dy:dy + height, dx:dx + width]
            return frame

        # 3.เลื่อนจากล่างขึ้นบนช้า ๆ (Slow Pan Up)
        def make_frame_3(t):
            progress = t / per_clip_duration
            h, w, _ = full_img.shape
            max_dy = h - height
            max_dx = w - width

            # เคลื่อนขึ้นแบบช้าลง (จากล่างขึ้นบน)
            dy = round((1 - progress) * max_dy * 0.25)

            # เคลื่อนขวานิดหน่อย
            dx = round((w - width) // 2 + progress * max_dx * 0.05)

            frame = full_img[dy:dy + height, dx:dx + width]
            return frame

        # 4.ซูมเข้า (Slow Zoom In)
        def make_frame_4(t):
            progress = t / per_clip_duration
            h, w, _ = full_img.shape

            scale = 1 + 0.2 * progress  # Zoom in 20%
            crop_h = int(height / scale)
            crop_w = int(width / scale)

            center_y = h // 2
            center_x = w // 2
            top = center_y - crop_h // 2
            left = center_x - crop_w // 2

            frame = full_img[top:top + crop_h, left:left + crop_w]
            frame = cv2.resize(frame, (width, height))
            return frame

        # 5.ซูมออก (Zoom Out)
        def make_frame_5(t):
            progress = t / per_clip_duration
            h, w, _ = full_img.shape

            scale = 1.2 - 0.2 * progress  # Zoom out from 120% → 100%
            crop_h = int(height / scale)
            crop_w = int(width / scale)

            center_y = h // 2
            center_x = w // 2
            top = center_y - crop_h // 2
            left = center_x - crop_w // 2

            frame = full_img[top:top + crop_h, left:left + crop_w]
            frame = cv2.resize(frame, (width, height))
            return frame


        motion_funcs = {
            0: make_frame_1,
            1: make_frame_2,
            2: make_frame_3,
            3: make_frame_4,
            4: make_frame_5,
        }

        make_frame = motion_funcs.get(count, make_frame_1)  # default fallback = zoom in
        clip = VideoClip(make_frame, duration=per_clip_duration).set_fps(fps)

        if idx > 0:
            clip = clip.crossfadein(fade_duration)
        clips.append(clip)

    if (num_images == 1): 
        # ซ้อน fade-in และหักช่วงซ้อนด้วย padding
        final_video = concatenate_videoclips(clips, method="compose")

    else: 
        # ซ้อน fade-in และหักช่วงซ้อนด้วย padding
        final_video = concatenate_videoclips(clips, method="compose", padding=-fade_duration)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video_path = temp_video.name
        final_video.write_videofile(
            temp_video_path,
            codec="libx264",                # H.264 รองรับกว้าง
            audio=False,                    # เปลี่ยนเป็น True ถ้ามีเสียง
            preset="veryslow",              # encode ช้าแต่คุณภาพสูง
            ffmpeg_params=[
                "-crf", "18",               # crf ต่ำ = คมชัด (0-51) ปกติ 18-23
                "-movflags", "+faststart"  # ทำให้เล่นเร็วบนเว็บ
            ],
            threads=4,                      # ปรับตาม CPU
            verbose=False,
            logger=None
        )

    # ปิด clip และ final เพื่อปลดล็อกไฟล์
    final_video.close()
    clip.close()


    with open(temp_video_path, "rb") as f:
        video_bytes = f.read()

    os.remove(temp_video_path)

    video_base64 = base64.b64encode(video_bytes).decode("utf-8")
    return video_base64