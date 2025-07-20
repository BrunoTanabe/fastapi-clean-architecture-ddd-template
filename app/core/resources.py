from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.core.database import init_database_client, close_database_client
from app.core.logging import init_loguru
from app.core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:  # noqa: ARG001
    await startup()
    try:
        yield
    finally:
        await shutdown()


async def startup() -> None:
    init_loguru()

    logger.info(f"Starting {settings.APPLICATION_TITLE}...")
    if settings.ENVIRONMENT == "DEV":
        logger.warning(
            "Running in development mode, this is not recommended for production!"
        )

    await init_database_client()
    logger.info("Database client initialized successfully.")

    logger.info(f"{settings.APPLICATION_TITLE} is ready to serve requests.")


async def shutdown() -> None:
    logger.info("Shutting down application...")

    await close_database_client()
    logger.info("Database client closed successfully.")

    logger.info(f"{settings.APPLICATION_TITLE} has been shut down successfully.")
