from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config.settings import settings


DATABASE_URL = (f"postgresql+asyncpg://{settings.postgres_user}:"
                f"{settings.postgres_password.get_secret_value()}@{settings.postgres_host}:"
                f"{settings.postgres_port}/{settings.postgres_db}")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session():
    async with AsyncSessionFactory() as session:
        yield session