# Example Dockerfile
FROM python:3.12-slim

# Install system dependencies needed by OpenCV
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

# Copy and install your Python packages
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of your app
COPY . .

# Run your app
CMD ["python", "main.py"]