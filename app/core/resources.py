from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.core.cache import (
    close_cache_client,
    flush_cache_namespace,
    init_cache_client,
)
from app.core.database import (
    init_database_client,
    close_database_client,
)
from app.core.logging import init_loguru
from app.core.migrations import init_alembic_management
from app.core.settings import settings
from app.modules.shared.domain.enums import ApplicationEnvironment
from app.modules.websocket.infrastructure.services import ConnectionManager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
    try:
        await startup(app)
        yield
    finally:
        await shutdown(app)


async def startup(app: FastAPI) -> None:
    try:
        init_loguru()
        logger.info(f"Starting {settings.APPLICATION_TITLE}...")

        if settings.APPLICATION_ENVIRONMENT == ApplicationEnvironment.DEV:
            logger.warning(
                "Running in development mode, this is not recommended for production!"
            )

            import ngrok

            logger.info("Initializing ngrok")
            ngrok.set_auth_token(settings.NGROK_AUTH_TOKEN)  # noqa

            listener = await ngrok.forward(addr=settings.APPLICATION_PORT)
            logger.info(f"Ngrok initialized successfully, public URL: {listener.url()}")

            app.mount("/devtools", StaticFiles(directory="scripts"), name="devtools")
            logger.info("Dev tools mounted at /devtools.")

        await init_database_client()
        logger.info("Database client initialized successfully.")

        await init_cache_client()
        logger.info("Cache client initialized successfully.")

        if settings.REDIS_FLUSH_ON_STARTUP:
            await flush_cache_namespace()
            logger.info("Cache namespace cleared on startup.")

        init_alembic_management()
        logger.info("Migration management initialized successfully.")

        app.state.connection_manager = ConnectionManager()  # noqa
        logger.info("WebSocket connection manager initialized successfully.")

        logger.info(f"{settings.APPLICATION_TITLE} is ready to serve requests.")
    except Exception as e:
        logger.opt(exception=e).error(
            f"An error occurred during startup of {settings.APPLICATION_TITLE}."
        )
        raise


async def shutdown(_app: FastAPI) -> None:
    try:
        logger.info("Shutting down application...")

        await close_cache_client()
        logger.info("Cache client closed successfully.")

        await close_database_client()
        logger.info("Database client closed successfully.")

        logger.info(f"{settings.APPLICATION_TITLE} has been shut down successfully.")
    except Exception as e:
        logger.opt(exception=e).error(
            f"An error occurred during shutdown of {settings.APPLICATION_TITLE}."
        )
        raise
