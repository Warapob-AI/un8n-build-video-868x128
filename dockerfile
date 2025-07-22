# ใช้ Python version 3.12 เป็น base image
FROM python:3.12-slim

# --- ใส่บรรทัดนี้ตรงนี้ ---
# ติดตั้ง system dependency ที่จำเป็นสำหรับ OpenCV
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

# กำหนดโฟลเดอร์ทำงานหลักใน container
WORKDIR /app

# คัดลอกไฟล์ requirements.txt เข้าไปก่อน
COPY requirements.txt .

# ติดตั้งไลบรารีของ Python
RUN pip install -r requirements.txt

# คัดลอกไฟล์อื่นๆ ทั้งหมดในโปรเจกต์เข้าไป
COPY . .

# คำสั่งสำหรับรันแอปพลิเคชัน (เปลี่ยน main.py เป็นชื่อไฟล์ของคุณ)
CMD ["python", "main.py"]