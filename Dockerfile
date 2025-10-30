FROM python:3.10-slim

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System packages for OCR (include language data)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Ensure Tesseract can find language data
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app code
COPY . .

# Expose port (used by Gunicorn)
EXPOSE 8000

# Start command
CMD ["bash", "start.sh"]
