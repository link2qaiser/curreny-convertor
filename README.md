# SpendingCrow

SpendingCrow is an expense tracking and personal finance management application built with FastAPI, PostgreSQL, and modern development tools.

## Project Structure

```
spending-crow/
├── .github/workflows/
│   └── main.yml
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── app/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt_handler.py
│   │   ├── routes.py
│   │   ├── service.py
│   │   ├── social.py
│   │   └── utils.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── profile/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── __init__.py
│   └── main.py
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.local.yml
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── poetry.lock
├── pyproject.toml
├── README.md
├── requirements.txt
└── requirements-dev.txt
```

## Prerequisites

- Docker and Docker Compose
- Make (for development commands)
- Poetry (for dependency management)
- Python 3.11+ (optional, for local development)

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/spending-crow.git
cd spending-crow
cp .env.example .env
# Edit .env file with your configuration
```

### 2. Start Development Environment

```bash
# Start all services (database, web app, pgadmin)
make server-up

# Run database migrations
make migrate

# Access the application
open http://localhost:8000
```

### 3. View Logs
```bash
make server-logs
```

## Development Commands

The project includes a comprehensive Makefile for easy development:

### 🐳 Server Management
```bash
make server-up        # Start development server
make server-down      # Stop development server
make server-restart   # Restart development server
make server-logs      # Show server logs
make server-clean     # Stop server and cleanup containers
```

### 🗄️ Database Migrations
```bash
make migrate          # Run database migrations
make migrate-down     # Rollback last migration
make migration msg="add user table"  # Create new migration
```

### 🧪 Testing
```bash
make test            # Run all tests
make test-cov        # Run tests with coverage
```

### 📦 Requirements Management
```bash
make requirements     # Generate requirements based on ENV_STATE from .env
                     # Dev: generates both requirements.txt and requirements-dev.txt
                     # Prod: generates only requirements.txt

make requirements-dev    # Always generate requirements-dev.txt (includes dev deps)
make requirements-prod   # Always generate requirements.txt (production only)
```

### 📋 Help
```bash
make help           # Show all available commands with descriptions
```

## Environment Configuration

The application uses environment-based configuration controlled by the `ENV_STATE` variable:

### Development (.env)
```bash
ENV_STATE=dev
DATABASE_URL=postgresql://postgres:password@db:5432/spendingcrow
API_URL=http://localhost:8000
POSTGRES_NAME=spendingcrow
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DATA_PATH=./postgres_data

# Authentication
JWT_SECRET_KEY=your_dev_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Social Auth Providers
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# PgAdmin
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=admin123
```

### Production
Production configuration is managed via GitHub Secrets and sets `ENV_STATE=prod`.

## Dependency Management

This project uses **Poetry** for dependency management with automatic environment-aware builds:

- **Development**: All dependencies including testing tools (pytest, coverage, etc.)
- **Production**: Only production dependencies for optimized containers

### Managing Dependencies

#### Adding Dependencies
```bash
# Add a production dependency
poetry add package-name

# Add a development dependency  
poetry add --group dev package-name

# Remove a dependency
poetry remove package-name
```

#### Generating Requirements Files
```bash
# Smart generation based on your .env ENV_STATE
make requirements

# Specific generation
make requirements-prod    # Production requirements only
make requirements-dev     # All dependencies including dev tools

# Or use Poetry directly
poetry export -f requirements.txt --output requirements.txt --without-hashes
poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes
```

#### Before Deployment
Always generate fresh requirements files before deploying:
```bash
make requirements-prod
git add requirements.txt
git commit -m "Update production requirements"
```

## Docker Configuration

### Smart Environment-Aware Builds
The Dockerfile automatically detects your environment and installs appropriate dependencies:

- **Development** (`ENV_STATE=dev`): Installs all dependencies from Poetry
- **Production** (`ENV_STATE=prod`): Installs only from requirements.txt

### Development Environment
- **File**: `docker-compose.local.yml`
- **Services**: PostgreSQL, PgAdmin, Web Application
- **Features**: Hot reloading, all dev dependencies, debugging tools

### Production Environment  
- **File**: `docker-compose.yml`
- **Services**: Web Application only
- **Features**: Optimized build, production dependencies only

## Database Access

### PgAdmin (Development)
- **URL**: http://localhost:8080
- **Email**: Value from `PGADMIN_DEFAULT_EMAIL`
- **Password**: Value from `PGADMIN_DEFAULT_PASSWORD`

### Direct PostgreSQL Access
```bash
# Access via Docker
docker compose -f docker-compose.local.yml exec db psql -U postgres -d spendingcrow
```

## API Documentation

When running, API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Deployment

The project uses GitHub Actions for automated deployment:

1. **Push to `dev` branch** triggers deployment
2. **Automatic deployment** to production server
3. **Database migrations** run automatically
4. **Environment variables** managed via GitHub Secrets

### Manual Deployment Commands
```bash
# On production server
docker compose down
docker compose up -d
docker compose exec -T spendingcrow alembic upgrade head
```

## Currency Rate Updates

SpendingCrow includes a secure endpoint for updating currency exchange rates:

```
POST /currency/update-rates
```

### Setup Automated Updates

1. **Add to `.env`**:
```bash
API_URL=https://spendingcrow.dixeam.com
OPENEXCHANGERATES_CRON_KEY=your_secure_cron_key
```

2. **Create update script** (`scripts/update-rates.sh`):
```bash
#!/bin/bash
set -o allexport
source .env
set +o allexport

curl -X 'POST' "$API_URL/currency/update-rates" \
  -H "accept: application/json" \
  -H "x-cron-key: ${OPENEXCHANGERATES_CRON_KEY}" \
  -d ''
```

3. **Setup cron job**:
```bash
0 * * * * /path/to/scripts/update-rates.sh >> /var/log/currency-update.log 2>&1
```

## Development Workflow

### Daily Development
```bash
# Start development environment
make server-up

# Make code changes...

# Add new dependencies if needed
poetry add new-package

# Update requirements for deployment
make requirements

# Create database migration
make migration msg="add new feature"

# Run migrations
make migrate

# Run tests
make test

# View logs
make server-logs
```

### Before Deployment
```bash
# Update production requirements
make requirements-prod

# Commit all changes
git add pyproject.toml poetry.lock requirements.txt
git commit -m "Add new feature and update dependencies"
git push origin dev  # Triggers automatic deployment
```

### Working with Dependencies
```bash
# Add a new production dependency
poetry add fastapi-users
make requirements-prod

# Add a new development tool
poetry add --group dev black
make requirements-dev

# Remove a dependency
poetry remove unused-package
make requirements

# Update all dependencies
poetry update
make requirements
```

## Troubleshooting

### Container Issues
```bash
# Rebuild containers
make server-down
docker compose -f docker-compose.local.yml build --no-cache
make server-up

# Clean up Docker resources
make server-clean
```

### Database Issues
```bash
# Reset database (WARNING: destroys data)
make server-down
docker volume rm spending-crow_postgres_data
make server-up
make migrate
```

### Dependency Issues
```bash
# Regenerate lock file
poetry lock

# Regenerate requirements files
make requirements

# Check for dependency conflicts
poetry check
```

### Logs and Debugging
```bash
# View application logs
make server-logs

# Access container shell
docker compose -f docker-compose.local.yml exec web bash

# Check installed packages in container
docker compose -f docker-compose.local.yml exec web pip list
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Install dependencies: `poetry install`
4. Make changes and test: `make test`
5. Update requirements: `make requirements`
6. Commit changes: `git commit -am 'Add new feature'`
7. Push to branch: `git push origin feature/new-feature`
8. Create Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.