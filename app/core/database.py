from typing import AsyncIterator, Iterator

from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, Session

from app.core.settings import settings
from app.modules.shared.presentation.exceptions import StandardException


# synchronous engine for migrations and initial setup
pg_engine = create_engine(
    settings.POSTGRESQL_DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.APPLICATION_ENVIRONMENT_DEBUG,
    connect_args={"options": "-c timezone=America/Sao_Paulo"},
    future=True,
)

PGSession = sessionmaker(
    pg_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_session() -> Iterator[Session]:
    session = PGSession()
    try:
        yield session
        session.commit()
    except StandardException:
        session.rollback()
        raise
    except SQLAlchemyError as e:
        logger.opt(exception=e).error("A database error occurred during the session.")
        session.rollback()
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An unexpected error occurred during the database session."
        )
        session.rollback()
        raise
    finally:
        session.close()


# asynchronous engine for FastAPI
pg_async_engine = create_async_engine(
    settings.POSTGRESQL_ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.APPLICATION_ENVIRONMENT_DEBUG,
    connect_args={"server_settings": {"timezone": "America/Sao_Paulo"}},
    future=True,
)

PGAsyncSession = async_sessionmaker(
    bind=pg_async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with PGAsyncSession() as session:
        try:
            yield session
            await session.commit()
        except StandardException:
            await session.rollback()
            raise
        except SQLAlchemyError as e:
            logger.opt(exception=e).error(
                "An asynchronous database error occurred during the session."
            )
            await session.rollback()
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the asynchronous database session."
            )
            await session.rollback()
            raise
        finally:
            await session.close()


# database connection for resources
async def init_database_client() -> None:
    try:
        logger.info("Establishing database connection.")

        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        async with pg_async_engine.connect() as async_conn:
            await async_conn.execute(text("SELECT 1"))

        logger.info("Database connection established successfully.")
    except StandardException:
        raise
    except SQLAlchemyError as e:
        logger.opt(exception=e).error(
            "An error occurred while initializing the database."
        )
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An unexpected error occurred while initializing the database."
        )
        raise


async def close_database_client() -> None:
    try:
        pg_engine.dispose()
        await pg_async_engine.dispose()

        logger.info("Database connection closed successfully.")
    except SQLAlchemyError as e:
        logger.opt(exception=e).error(
            "An error occurred while closing the database connection."
        )
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An unexpected error occurred while closing the database connection."
        )
        raise
