# Medical Report Scanner

A Django-based application for scanning and processing medical reports using OCR (Optical Character Recognition) with support for multiple OCR engines including table extraction capabilities.

## Features

- Image processing and OCR for medical reports
- **Table extraction** using PaddleOCR's TableRecognitionPipelineV2
- Multiple OCR engines: Tesseract, PaddleOCR, and PaddleTable
- **Memory-optimized** processing with image resizing and garbage collection
- **Shared model storage** to reduce memory usage and startup time
- PostgreSQL database for data storage
- Redis for caching
- Docker containerization for easy deployment

## Prerequisites

- Docker
- Docker Compose
- **Minimum 4GB RAM** (8GB+ recommended for optimal performance)

## Quick Start

### Production Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd img_medreport_scanner
```

2. Build and start the services:

```bash
docker-compose up --build
```

**Note**: First startup may take several minutes as OCR models are downloaded to the shared volume.

3. Create a superuser (in a new terminal):

```bash
docker-compose exec web python manage.py createsuperuser
```

4. Access the application:
   - OCR API: http://localhost:8000/ocr/

### Development Setup

For development with live code reloading:

```bash
docker-compose -f docker-compose.dev.yml up --build
```

## API Usage

### OCR Endpoint

**POST** `/ocr/`

Extract text from medical report images using OCR.

#### Request

- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `image` (required): Image file (JPEG, PNG, TIFF, etc.)
  - `model` (optional): OCR engine to use (`Tesseract`, `PaddleOCR`, or `PaddleTable`). Defaults to `Tesseract`.

#### Example Request

```bash
# Standard text extraction
curl -X POST http://localhost:8000/ocr/ \
  -F "image=@medical_report.jpg" \
  -F "model=Tesseract"

# Table extraction
curl -X POST http://localhost:8000/ocr/ \
  -F "image=@medical_report_with_table.jpg" \
  -F "model=PaddleTable"
```

#### Response

**Standard OCR Response:**

```json
{
  "text": "Extracted text from the image...",
  "average_confidence": 87.5
}
```

**Table OCR Response:**

```json
{
  "text": "Extracted text from the image...",
  "average_confidence": 87.5,
  "tables": ["<table>...</table>", "<table>...</table>"]
}
```

#### Error Response

```json
{
  "error": "Error message",
  "status": "initializing" // Only for PaddleOCR/PaddleTable when still initializing
}
```

### OCR Engines

#### Tesseract

- **Default engine**: Fast and reliable
- **Language**: English
- **Confidence**: Word-level confidence scores
- **Status**: Always ready
- **Memory usage**: Low

#### PaddleOCR

- **Advanced engine**: Better accuracy for complex layouts
- **Language**: English
- **Confidence**: Word-level confidence scores
- **Status**: Initializes on service startup
- **Memory usage**: Medium to High
- **Optimizations**: Image resizing, garbage collection

#### PaddleTable

- **Table extraction engine**: Specialized for table detection and extraction
- **Technology**: PaddleOCR's TableRecognitionPipelineV2
- **Output**: HTML table format
- **Status**: Initializes on service startup
- **Memory usage**: High (requires more memory for table processing)
- **Optimizations**: Image resizing, garbage collection, memory management

## Services

- **Web**: Django application (port 8000)
- **Database**: PostgreSQL 15 (port 5432)
- **Cache**: Redis 7 (port 6379)
- **Model Downloader**: Downloads OCR models to shared volume (runs once)

## Architecture

### Model Management

- **Shared Volume**: OCR models are downloaded once to a shared Docker volume
- **Caching**: Compiled model components are cached using ccache
- **Memory Optimization**: Models are loaded only when needed

### Memory Management

- **Image Resizing**: Large images are automatically resized to reduce memory usage
- **Garbage Collection**: Explicit garbage collection after OCR processing
- **Synchronous Processing**: OCR runs synchronously (Celery disabled) to reduce memory overhead

## Environment Variables

You can customize the following environment variables:

- `DEBUG`: Set to 'True' for development, 'False' for production
- `SECRET_KEY`: Django secret key
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

## Database

The application uses PostgreSQL in production and SQLite in development. Database migrations are automatically applied when the container starts.

## Static Files

Static files are collected to the `staticfiles` directory and served by the web server.

## Development Commands

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic

# Run tests
docker-compose exec web python manage.py test

# Access Django shell
docker-compose exec web python manage.py shell

# Check shared model volume contents
docker-compose exec web ls -la /app/shared_models/
```

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (this will delete the database and shared models)
docker-compose down -v
```

## Troubleshooting

1. **Port conflicts**: Make sure ports 8000, 5432, and 6379 are available
2. **Permission issues**: The application runs as a non-root user inside the container
3. **Database connection**: Ensure the database service is running before starting the web service
4. **OCR initialization**: First startup may take time as models are downloaded to shared volume
5. **Memory issues**:
   - Ensure Docker has sufficient memory (4GB+ recommended, 8GB+ for optimal performance)
   - Large images are automatically resized to reduce memory usage
   - Check Docker Desktop memory allocation settings
6. **Model download issues**: Check if the model-downloader service completed successfully
7. **Table extraction failures**: Ensure sufficient memory is available for PaddleTable engine

## Performance Tips

- **Memory**: Allocate at least 4GB RAM to Docker (8GB+ recommended)
- **Storage**: Use SSD storage for better model loading performance
- **Images**: Pre-resize very large images (>10MB) before uploading
- **Concurrent requests**: Limit concurrent OCR requests to prevent memory exhaustion

## Project Structure

```
img_medreport_scanner/
├── Dockerfile                 # Docker image definition with ccache
├── docker-compose.yml         # Production Docker Compose with model sharing
├── docker-compose.dev.yml     # Development Docker Compose
├── requirements.txt           # Python dependencies
├── .dockerignore             # Files to exclude from Docker build
├── manage.py                 # Django management script
├── img_medreport_scanner/    # Django project settings
│   ├── __init__.py           # App initialization (OCR engine setup)
│   ├── settings.py           # Django settings
│   ├── urls.py              # URL configuration
│   ├── wsgi.py              # WSGI configuration
│   ├── asgi.py              # ASGI configuration
│   └── celery.py            # Celery configuration (disabled)
├── ocr/                      # OCR application
│   ├── engines/              # OCR engine implementations
│   │   ├── base.py          # Base OCR engine interface
│   │   ├── factory.py       # OCR engine factory
│   │   ├── tesseract_engine.py
│   │   ├── paddle_ocr_engine.py
│   │   └── paddle_table_ocr_engine.py
│   ├── models.py            # Database models
│   ├── views.py             # OCR API views
│   ├── serializers.py       # Request/response serializers
│   └── urls.py              # URL routing
└── README.md                # This file
```

## Dependencies

### Core Dependencies

- Django 5.2.3
- Django REST Framework
- Pillow (image processing)
- pytesseract (Tesseract OCR)
- paddleocr (PaddleOCR engine)
- paddlepaddle (PaddlePaddle framework)
- numpy (numerical operations)

### Infrastructure

- PostgreSQL 15
- Redis 7
- Gunicorn (production server)
- ccache (compilation caching)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker
5. Submit a pull request

## License

[Add your license information here]
