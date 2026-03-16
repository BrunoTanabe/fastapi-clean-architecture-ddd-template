from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.core.database import (
    init_database_client,
    close_database_client,
)
from app.core.logging import init_loguru
from app.core.migrations import init_alembic_management
from app.core.key_management import init_security_keys
from app.core.settings import settings
from app.modules.shared.application.enums import ApplicationEnvironment


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
    try:
        await startup(app)
        yield
    finally:
        await shutdown()


async def startup(app: FastAPI) -> None:
    try:
        init_loguru()
        logger.info(f"Starting {settings.APPLICATION_TITLE}...")

        if (
            not settings.APPLICATION_ENVIRONMENT
            == ApplicationEnvironment.PRODUCTION.value
        ):
            logger.warning(
                f"Running in development mode, in {settings.APPLICATION_ENVIRONMENT} environment. This is not recommended for production!"
            )

        await init_database_client()
        logger.info("Database client initialized successfully.")

        await init_security_keys()
        logger.info("Security keys initialized successfully.")

        await init_alembic_management()
        logger.info("Migration management initialized successfully.")

        logger.info(f"{settings.APPLICATION_TITLE} is ready to serve requests.")
    except Exception as e:
        logger.opt(exception=e).error(
            f"An error occurred during startup of {settings.APPLICATION_TITLE}."
        )
        raise


async def shutdown() -> None:
    try:
        logger.info("Shutting down application...")

        await close_database_client()
        logger.info("Database client closed successfully.")

        logger.info(f"{settings.APPLICATION_TITLE} has been shut down successfully.")
    except Exception as e:
        logger.opt(exception=e).error(
            f"An error occurred during shutdown of {settings.APPLICATION_TITLE}."
        )
        raise
