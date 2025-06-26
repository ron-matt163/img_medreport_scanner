# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=img_medreport_scanner.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libopencv-dev \
        python3-opencv \
        libgl1-mesa-glx \
        libglib2.0-0 \
        tesseract-ocr \
        ccache \
    && rm -rf /var/lib/apt/lists/*

# Configure ccache for PaddleOCR optimization
ENV CCACHE_DIR=/home/appuser/.ccache
ENV CCACHE_MAXSIZE=2G
ENV PATH="/usr/lib/ccache:${PATH}"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

# Create PaddleOCR directory and set permissions
RUN mkdir -p /home/appuser/.paddlex && \
    chown -R appuser:appuser /home/appuser/.paddlex

RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "img_medreport_scanner.wsgi:application"] 