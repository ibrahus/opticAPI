from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from app.models import Base

# Load environment variables
load_dotenv()

# Database configurations
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/optic_db")

if DATABASE_URL:
    # Convert string URL to URL object, which helps in proper handling of parameters
    url = URL.create(DATABASE_URL, query={"sslmode": "disable"})

    # Replace 'postgresql://' with 'postgresql+asyncpg://'
    if url.drivername == "postgresql":
        url = url.set(drivername="postgresql+asyncpg")

    engine = create_async_engine(url, echo=False)
else:
    raise ValueError("No DATABASE_URL found in environment variables")

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
