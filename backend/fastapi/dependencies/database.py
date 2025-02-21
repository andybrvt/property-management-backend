from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from backend.fastapi.core.init_settings import global_settings as settings

# Base class for the database models
Base = declarative_base()

# Synchronous engine and session

sync_engine = create_engine(settings.DB_URL)  # Alembic will use this engine
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Asynchronous engine and session (for async operations in your app, but not for Alembic)
async_engine = create_async_engine(settings.ASYNC_DB_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)

# Remove init_db since Alembic should handle database migrations
# Alembic uses migration scripts instead of `Base.metadata.create_all()` for schema creation

def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
