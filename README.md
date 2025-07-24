# Currency Converter

A real-time currency converter application built with FastAPI that provides up-to-date exchange rates and seamless currency conversion between multiple international currencies.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Development Commands](#development-commands)
- [Features](#features)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Database Management](#database-management)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Installation

```bash
# Clone the repository
git clone https://github.com/username/currency-converter.git

# Navigate to project directory
cd currency-converter

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start the development environment
make server-up
```

## Usage

### Quick Start

```bash
# Show all available commands
make help

# Start the FastAPI development server
make server-up

# Visit http://localhost:8000 for the web interface
# Visit http://localhost:8000/docs for API documentation
```

## Development Commands

The project includes a comprehensive Makefile with colored output for easy development:

### 🐳 Server Management

```bash
make server-up        # Start the development server
make server-down      # Stop the development server  
make server-restart   # Restart the development server
make server-logs      # Show server logs
make server-clean     # Stop server and clean up containers
```

### 🗄️ Database Migrations

```bash
make migrate-up       # Upgrade one revision (+1)
make migrate-up-all   # Upgrade all migrations to head
make migrate-down     # Downgrade one revision (-1)
make migrate-down-all # Downgrade all the way to base
```

### 🧪 Testing

```bash
make test            # Run all tests
make test-cov        # Run tests with coverage report
```

### 📦 Requirements Management

```bash
make requirements       # Generate requirements based on ENV_STATE
                       # Dev: generates both requirements.txt and requirements-dev.txt
                       # Prod: generates only requirements.txt

make requirements-dev   # Generate requirements-dev.txt (includes dev dependencies)
make requirements-prod  # Generate requirements.txt (production only)
```

### Getting Help

```bash
make help              # Show all available commands with descriptions
```

## Features

- **Real-time Exchange Rates**: Fetches current exchange rates from reliable APIs
- **Multi-Currency Support**: Supports 150+ international currencies
- **FastAPI Backend**: High-performance async API with automatic documentation
- **Database Migrations**: Alembic-powered database schema management
- **Docker Development**: Containerized development environment
- **Automated Testing**: Comprehensive test suite with coverage reporting
- **Poetry Integration**: Modern Python dependency management
- **Environment-Aware**: Smart development/production configuration

## API Documentation

When the server is running, comprehensive API documentation is available:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

- `GET /` - Web interface home page
- `GET /api/rates` - Get current exchange rates
- `GET /api/convert?from=USD&to=EUR&amount=100` - Convert currency
- `GET /api/currencies` - List supported currencies
- `GET /api/historical?date=2024-01-01&from=USD&to=EUR` - Historical rates

### Example API Usage

```bash
# Get current rates
curl "http://localhost:8000/api/rates"

# Convert currency
curl "http://localhost:8000/api/convert?from=USD&to=EUR&amount=100"

# Get supported currencies
curl "http://localhost:8000/api/currencies"
```

### Example Response

```json
{
  "from": "USD",
  "to": "EUR",
  "amount": 100,
  "result": 85.23,
  "rate": 0.8523,
  "timestamp": "2024-01-15T10:30:00Z",
  "provider": "ExchangeRate-API"
}
```

## Configuration

### Environment Variables

Copy the example environment file and configure it:

```bash
# Copy the example file
cp .env.example .env

# Edit with your actual values
nano .env
```

The `.env.example` file contains all required configuration variables:

```env
# Environment Configuration
ENV_STATE=dev
API_URL=http://localhost:8000

# Database Configuration
POSTGRES_NAME=currency_convertor
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password_here
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_NAME}
POSTGRES_DATA_PATH=/path/to/your/databases/currency_convertor

# PgAdmin Configuration
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=your_pgadmin_password_here

# Internal API Key
API_KEY=your_internal_api_key_here

# Open Exchange Rates API
OPENEXCHANGERATES_API_KEY=your_openexchangerates_api_key_here
OPENEXCHANGERATES_CRON_KEY=your_secure_cron_key_here

# CoinMarketCap API
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key_here

# Digital Ocean Spaces (S3) Configuration
DO_SPACES_ENDPOINT=https://your-region.digitaloceanspaces.com
DO_SPACES_REGION=your_region
DO_SPACES_KEY=your_do_spaces_key_here
DO_SPACES_SECRET=your_do_spaces_secret_here
DO_SPACES_BUCKET=your_bucket_name
DO_SPACES_CDN_URL=https://your-region.digitaloceanspaces.com/your_bucket_name

# Job Intervals (in minutes)
WRITE_FILE_ON_S3=60
FETCH_API_DATA=60
```

### Required API Keys

To fully configure the application, you'll need to obtain API keys from:

1. **Open Exchange Rates**: [https://openexchangerates.org/](https://openexchangerates.org/)
   - Sign up for a free account to get `OPENEXCHANGERATES_API_KEY`
   - Generate a secure cron key for `OPENEXCHANGERATES_CRON_KEY`

2. **CoinMarketCap**: [https://coinmarketcap.com/api/](https://coinmarketcap.com/api/)
   - Register for API access to get `COINMARKETCAP_API_KEY`

3. **Digital Ocean Spaces** (Optional): [https://www.digitalocean.com/products/spaces/](https://www.digitalocean.com/products/spaces/)
   - Set up a Spaces bucket for file storage
   - Get access key and secret for S3-compatible storage

### Docker Configuration

The project uses Docker Compose for development with the following configuration:

```yaml
# docker-compose.local.yml
services:
  - Web application (FastAPI) - Port 8000
  - PostgreSQL database - Port 5432  
  - PgAdmin (database management) - Port 8080
```

**Important**: The Docker configuration uses environment variables from your `.env` file:
- `POSTGRES_DATA_PATH` determines where database data is stored on your host
- `POSTGRES_NAME`, `POSTGRES_USER`, `POSTGRES_PASSWORD` configure the database
- `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD` set up PgAdmin access

## Database Management

### Migration Commands

The project uses Alembic for database migrations:

```bash
# Apply all pending migrations
make migrate-up-all

# Apply one migration
make migrate-up

# Rollback one migration
make migrate-down

# Rollback to base (WARNING: destroys data)
make migrate-down-all
```

### Creating New Migrations

```bash
# Access the container to create migrations
docker compose -f docker-compose.local.yml exec web bash

# Inside the container
alembic revision --autogenerate -m "description of changes"

# Then apply the migration
make migrate-up
```

### Database Access

Access the database directly:

```bash
# Via PgAdmin web interface
# Visit http://localhost:8080 (credentials in .env)

# Via command line
docker compose -f docker-compose.local.yml exec db psql -U postgres -d currency_converter
```

## Development

### Prerequisites

- Docker and Docker Compose
- Make (for development commands)
- Poetry (for dependency management)
- Python 3.11+ (optional, for local development)

### Development Workflow

```bash
# 1. Start the development environment
make server-up

# 2. Make code changes...

# 3. View logs to debug
make server-logs

# 4. Run tests
make test

# 5. Add new dependencies (if needed)
poetry add new-package

# 6. Update requirements
make requirements

# 7. Create database migration (if schema changed)
# Access container and run: alembic revision --autogenerate -m "description"

# 8. Apply migrations
make migrate-up

# 9. Restart server to see changes
make server-restart
```

### Adding Dependencies

```bash
# Add a production dependency
poetry add fastapi-new-feature

# Add a development dependency  
poetry add --group dev pytest-new-tool

# Update requirements files
make requirements

# Remove a dependency
poetry remove unused-package
```

### Project Structure

```
currency-converter/
├── .github/workflows/     # CI/CD workflows
├── alembic/              # Database migrations
│   └── versions/         # Migration files
├── app/                  # Main application code
│   ├── api/             # API endpoints
│   ├── core/            # Core configuration
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   └── services/        # Business logic
├── tests/               # Test files
├── docker-compose.local.yml
├── Dockerfile
├── Makefile            # Development commands
├── pyproject.toml      # Poetry configuration
├── requirements.txt    # Production dependencies
└── requirements-dev.txt # Development dependencies
```

### Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# View coverage report
# Open htmlcov/index.html in browser after running test-cov
```

### Troubleshooting

#### Container Issues
```bash
# Clean up and rebuild
make server-clean
make server-up
```

#### Database Issues
```bash
# Reset database (WARNING: destroys data)
make server-down
docker volume rm currency-converter_postgres_data
make server-up
make migrate-up-all
```

#### Dependency Issues
```bash
# Regenerate Poetry lock file
poetry lock

# Update requirements
make requirements
```





## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [ExchangeRate-API](https://exchangerate-api.com/) for providing exchange rate data
- [Poetry](https://python-poetry.org/) for dependency management
- [Alembic](https://alembic.sqlalchemy.org/) for database migrations
- Contributors and community members