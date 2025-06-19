# Medical Report Scanner

A Django-based application for scanning and processing medical reports using computer vision and AI.

## Features

- Image processing and OCR for medical reports
- PostgreSQL database for data storage
- Redis for caching and background tasks
- Celery for asynchronous task processing
- Docker containerization for easy deployment

## Prerequisites

- Docker
- Docker Compose

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

3. Create a superuser (in a new terminal):

```bash
docker-compose exec web python manage.py createsuperuser
```

4. Access the application:
   - Web application: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

### Development Setup

For development with live code reloading:

```bash
docker-compose -f docker-compose.dev.yml up --build
```

## Services

- **Web**: Django application (port 8000)
- **Database**: PostgreSQL 15 (port 5432)
- **Cache**: Redis 7 (port 6379)
- **Celery**: Background task worker

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

## Background Tasks

Celery is configured for background task processing. Tasks can be defined in your Django apps and will be automatically discovered.

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
```

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (this will delete the database)
docker-compose down -v
```

## Troubleshooting

1. **Port conflicts**: Make sure ports 8000, 5432, and 6379 are available
2. **Permission issues**: The application runs as a non-root user inside the container
3. **Database connection**: Ensure the database service is running before starting the web service

## Project Structure

```
img_medreport_scanner/
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Production Docker Compose
├── docker-compose.dev.yml     # Development Docker Compose
├── requirements.txt           # Python dependencies
├── .dockerignore             # Files to exclude from Docker build
├── manage.py                 # Django management script
├── img_medreport_scanner/    # Django project settings
│   ├── __init__.py
│   ├── settings.py           # Django settings
│   ├── urls.py              # URL configuration
│   ├── wsgi.py              # WSGI configuration
│   ├── asgi.py              # ASGI configuration
│   └── celery.py            # Celery configuration
└── README.md                # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker
5. Submit a pull request

## License

[Add your license information here]
