from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import env_var

# SQLAlchemy base
Base = declarative_base()

# Async engine
engine = create_async_engine(
    env_var.DATABASE_URL,
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
