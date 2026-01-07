# GRA Background Services

Background services for the Gordon Ramsay Academy platform, built on the Kimera framework. This service handles asynchronous tasks, scheduled jobs, email communications, and event processing.

## Architecture

The service uses the Kimera framework with the following components:
- **Bootstrap**: Orchestrates API, Intercom, Kafka, Celery, and data stores
- **FastAPI**: Main API server (runs via Bootstrap in `main.py`)
- **Celery**: Distributed task queue for background jobs
- **Redis**: Cache, blackboard, and message broker
- **MongoDB**: Default document store
- **PostgreSQL**: Primary relational database

## Environment Variables

### Core Configuration

#### Application Settings
```bash
EXTERNAL_PORT=8888                     # External API port
COMPOSE_BAKE=true                      # Docker compose bake mode
```

#### Feature Flags
```bash
API=1                                  # Enable FastAPI server (1=enabled, 0=disabled)
KAFKA=0                                # Enable Kafka integration (1=enabled, 0=disabled)
CELERY=1                               # Enable Celery workers (1=enabled, 0=disabled)
```

### Data Stores

#### MongoDB
```bash
DEFAULT_STORE=mongodb://host.docker.internal:27007/default_db
```
- **Purpose**: Default document store for flexible schema data
- **Format**: `mongodb://[host]:[port]/[database]`
- **Default**: Uses Docker internal host on port 27007

#### PostgreSQL
```bash
POSTGRES_STORE=postgresql+asyncpg://[user]:[password]@[host]:[port]/[database]
```
- **Purpose**: Primary relational database (shared with gra-alkhaleej)
- **Driver**: asyncpg for async operations
- **Example**: `postgresql+asyncpg://gramsey_user:password@172.17.0.1:5432/gramsey_db`

### Redis Connections

Multiple Redis databases for different purposes:

```bash
REDIS_CACHE=redis://172.17.0.1:6379/cache          # General caching
REDIS_BLACKBOARD=redis://172.17.0.1:6379/blackboard # Shared state/messaging
REDIS_COMM=redis://172.17.0.1:6379/comm            # Communication queue
RESULT_BACKEND=redis://172.17.0.1:6379/0           # Celery results
BROKER_URL=redis://172.17.0.1:6379/0               # Celery broker
PUBSUB_URL=redis://172.17.0.1:6379/1               # Pub/Sub messaging
COMM_QUEUE=redis://172.17.0.1:6379/9               # Communication tasks
```

**Note**: Each Redis database number (0-9) serves a specific purpose to isolate data.

### Kafka (Optional)

```bash
KAFKA=0                                # Enable/disable Kafka
KAFKA_SERVER_1=kafka:9092              # Kafka broker address
```
- **Purpose**: Event streaming and message processing
- **Default**: Disabled (set to 1 to enable)

### Email Service

```bash
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxx
```
- **Purpose**: Resend.com API key for transactional emails
- **Required**: Yes, for sending emails (activation, notifications, etc.)
- **Get Key**: https://resend.com/api-keys

### CORS Configuration

```bash
ORIGINS=http://localhost:5173,http://localhost:8765
```
- **Purpose**: Allowed origins for CORS
- **Format**: Comma-separated list of URLs
- **Common**: Frontend dev servers, admin panels

### API Authentication (Optional)

```bash
API_GITHUB=username:token              # GitHub API credentials
KIMP_TOKEN=username:token              # Kimera platform token
```
- **Purpose**: External API integrations
- **Required**: Only if using GitHub or Kimera integrations

### OAuth Providers (Optional)

All OAuth settings are optional and only needed if implementing social login:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8031/api/auth/oauth/google/callback/

# Meta (Facebook) OAuth
META_CLIENT_ID=your_client_id
META_CLIENT_SECRET=your_client_secret
META_REDIRECT_URI=http://localhost:8031/api/auth/oauth/meta/callback/

# OAuth Callback
OAUTH_CALLBACK_URL=http://localhost:3001/oauth/bridge
```

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Start Required Services

Ensure the following services are running:
- **PostgreSQL**: Port 5432 (shared with gra-alkhaleej)
- **Redis**: Port 6379
- **MongoDB**: Port 27007 (if using DEFAULT_STORE)

### 4. Run the Service

```bash
# Start the FastAPI server
python app/main.py

# Or start Celery worker
celery -A app.celery worker --loglevel=info
```

## Docker Deployment

```bash
# Build image
docker build -t gra-bg-services .

# Run container
docker run -d \
  --name gra-bg-services \
  --env-file .env \
  -p 8888:8888 \
  gra-bg-services
```

## Key Features

- **Email Processing**: Transactional emails via Resend API
- **Background Jobs**: Celery-based task queue
- **Scheduled Tasks**: Cron-like job scheduling
- **Event Processing**: Kafka integration (optional)
- **Caching**: Redis-based caching layer
- **API Endpoints**: FastAPI REST endpoints

## Documentation

For detailed Kimera framework documentation, see `docs/kimera/` which mirrors the module layout.

## Related Services

- **gra-alkhaleej**: Main NestJS backend (shares PostgreSQL database)
- **gra-bff**: Backend for Frontend (GraphQL layer)
- **GRA_FE_WEB**: Customer-facing Next.js frontend
- **gra-lms**: Admin LMS Next.js application
