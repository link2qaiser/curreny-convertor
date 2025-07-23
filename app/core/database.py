from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import env_var

# SQLAlchemy base
Base = declarative_base()

# Convert DATABASE_URL to use asyncpg for async operations
database_url = env_var.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

# Async engine
engine = create_async_engine(
    database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Async session factory
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
