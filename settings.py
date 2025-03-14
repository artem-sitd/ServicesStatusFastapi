import os
from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

env_file = (
    Path(__file__).parent / ".env.docker"
    if os.getenv("USE_DOCKER")
    else Path(__file__).parent / ".env"
)


class DatabaseEnv(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore", env_file=env_file, env_file_encoding="utf-8"
    )
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str


class DatabaseConnect(BaseSettings):
    db_env: ClassVar[DatabaseEnv] = DatabaseEnv()
    db_url: ClassVar[
        str
    ] = f"postgresql+asyncpg://{db_env.POSTGRES_USER}:{db_env.POSTGRES_PASSWORD}@{db_env.POSTGRES_HOST}/{db_env.POSTGRES_DB}"

    engine: ClassVar = create_async_engine(db_url)
    async_session: ClassVar = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async def get_session(self) -> AsyncSession:
        async with self.async_session() as session:
            yield session


db_settings = DatabaseConnect()
