# File: README.md
# Sense Street API

A FastAPI-based REST API for uploading and processing chat files in a SaaS context.

## Features

- Upload single or multiple chat files (JSON/CSV)
- Asynchronous file processing simulation
- Multi-tenant customer isolation
- RESTful API with automatic OpenAPI documentation
- Progress tracking and status monitoring
- Dashboard analytics

## Quick Start

### Prerequisites
- Docker (recommended for easy and secure replicability)
- (Optional) Python 3.11 if you want to run locally without Docker

### Running with Docker

1. Clone the repository
```bash
# Replace <repository-url> with your repo URL
git clone <repository-url>
cd sense-street-tht
```

2. Build the Docker image
```bash
docker build -t sense-street-api .
```

3. Run the container
```bash
docker run -p 8000:8000 sense-street-api
```

The API will be available at `http://localhost:8000`

### (Optional) Local Python Setup
If you prefer not to use Docker, you can still run locally:
```bash
pip install -r requirements.txt
python main.py
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### Core Functionality

#### Upload Files
```http
POST /api/v1/uploads
Content-Type: multipart/form-data

customer_id: string
files: file[]
```

**Example Response:**
```json
{
  "message": "Successfully uploaded 2 files",
  "uploads": [
    {
      "id": "uuid-here",
      "customer_id": "customer123",
      "filename": "chat_export.json",
      "file_type": "json",
      "file_size": 1024,
      "upload_timestamp": "2024-01-15T10:30:00Z",
      "status": "pending",
      "progress": 0
    }
  ]
}
```

#### Get Processing Results
```http
GET /api/v1/uploads/{upload_id}/results?customer_id=customer123
```

**Example Response:**
```json
{
  "upload_id": "uuid-here",
  "results": [
    {
      "result_type": "sentiment_analysis",
      "data": {
        "overall_sentiment": "positive",
        "sentiment_score": 0.75,
        "positive_messages": 45,
        "negative_messages": 10,
        "neutral_messages": 35
      },
      "created_at": "2024-01-15T10:35:00Z"
    }
  ]
}
```

### Additional Endpoints

#### List Uploads
```http
GET /api/v1/uploads?customer_id=customer123&skip=0&limit=10&status=completed
```

#### Check Upload Status
```http
GET /api/v1/uploads/{upload_id}/status?customer_id=customer123
```

#### Dashboard Summary
```http
GET /api/v1/dashboard/summary?customer_id=customer123
```

#### Health Check
```http
GET /api/v1/health
```

#### Delete Upload
```http
DELETE /api/v1/uploads/{upload_id}?customer_id=customer123
```

## Testing with Postman

### 1. Upload a File
- Method: POST
- URL: `http://localhost:8000/api/v1/uploads`
- Body: form-data
  - Key: `customer_id`, Value: `test_customer`
  - Key: `files`, Type: File, Value: select your JSON/CSV file

### 2. Check Status
- Method: GET
- URL: `http://localhost:8000/api/v1/uploads/{upload_id}/status?customer_id=test_customer`

### 3. Get Results
- Method: GET
- URL: `http://localhost:8000/api/v1/uploads/{upload_id}/results?customer_id=test_customer`

## File Format Examples

### JSON Chat File
```json
[
  {
    "sender": "user1",
    "message": "Hello there!",
    "timestamp": "2024-01-15T10:00:00Z"
  },
  {
    "sender": "user2", 
    "message": "Hi! How are you?",
    "timestamp": "2024-01-15T10:01:00Z"
  }
]
```

### CSV Chat File
```csv
sender,message,timestamp
user1,"Hello there!","2024-01-15T10:00:00Z"
user2,"Hi! How are you?","2024-01-15T10:01:00Z"
```

## Architecture Overview

### Project Structure
```
main.py                    # FastAPI application and route definitions
config.py                  # Configuration management
dependencies.py            # Dependency injection setup
models/
  ├── schemas.py           # Pydantic models for requests/responses
  └── database.py          # In-memory database implementation
services/
  ├── upload_service.py    # Upload business logic
  └── processing_service.py# File processing logic
test_files/                # Example chat files for testing
requirements.txt           # Python dependencies
Dockerfile                 # Docker container definition
```

### Key Design Decisions

1. **Clean Architecture**: Separation of concerns with services, models, and dependencies
2. **Async Processing**: Background file processing with progress tracking
3. **Multi-tenancy**: Customer isolation through customer_id parameter
4. **Error Handling**: Comprehensive error handling with appropriate HTTP status codes
5. **Validation**: File type and size validation using Pydantic models

## Production Considerations

### Scalability
- **Database**: Replace in-memory storage with PostgreSQL + connection pooling
- **File Storage**: Use Supabase Storage or AWS S3 for file persistence
- **Processing**: Implement with Celery + Redis for distributed processing
- **Caching**: Add Redis caching for frequently accessed results
- **Load Balancing**: Horizontal scaling with multiple API instances

### Security
- **Authentication**: Implement API key or OAuth2 authentication
- **Authorization**: Row-level security for true multi-tenant isolation
- **Validation**: Enhanced input sanitization and file scanning
- **Rate Limiting**: Implement rate limiting per customer
- **HTTPS**: SSL/TLS encryption for all endpoints

### Monitoring & Operations
- **Logging**: Structured logging with correlation IDs
- **Metrics**: Application metrics (response times, error rates, upload volumes)
- **Health Checks**: Database and external service connectivity checks
- **Error Tracking**: Integration with Sentry or similar service
- **Observability**: Distributed tracing for complex request flows

### Data Management
- **Migrations**: Database schema versioning 
- **Backups**: Automated backup strategies for uploaded files and results
- **Retention**: Configurable data retention policies
- **Compliance**: GDPR/privacy compliance features (data export, deletion)

### Additional SaaS Features
- **Webhook Integration**: Notify customers when processing completes
- **Batch Processing**: Bulk upload and processing capabilities
- **Analytics Dashboard**: Rich analytics and reporting features
- **API Versioning**: Support for multiple API versions
- **Usage Tracking**: Monitor and bill based on usage metrics

## Assumptions & Simplifications

1. **In-Memory Storage**: Using in-memory database for simplicity (easily replaceable)
2. **Mock Processing**: Simulated sentiment analysis and metrics generation
3. **Simple Authentication**: Customer ID passed as parameter (would use API keys in production)
4. **File Validation**: Basic format validation (would add virus scanning in production)
5. **Error Handling**: Simplified error responses (would include detailed logging in production)


## Docker Notes

- All dependencies and code are isolated and reproducible in the Docker container.
- No need for a local Python virtual environment.
- `.env.example` is not required, but you can create a `.env` file if you want to override config values (see `config.py`).