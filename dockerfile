FROM n8nio/n8n:1.97.1 

# 🔐 เปลี่ยนเป็น root ก่อนติดตั้ง
USER root

# ติดตั้ง Python และ pip ใน Alpine
RUN apk update && apk add --no-cache python3 py3-pip

# ติดตั้งไลบรารี Python ที่ต้องการ
RUN pip3 install --break-system-packages moviepy==1.0.3 fastapi Pillow 

# 🔄 กลับมาเป็น user node (เพื่อความปลอดภัย/ไม่ให้ n8n รันด้วย root)
USER node

ENV PYTHONUNBUFFERED=1