from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from loguru import logger
from sqlalchemy import inspect, text

from app.core.database import pg_engine
from app.modules.shared.presentation.exceptions import StandardException


async def init_alembic_management() -> None:
    try:
        logger.info("Checking Alembic migration status...")

        alembic_cfg = Config("alembic.ini")

        inspector = inspect(pg_engine)
        has_alembic_table = "alembic_version" in inspector.get_table_names()

        if not has_alembic_table:
            logger.warning(
                "Alembic version table not found. Initializing management..."
            )

            logger.info("Empty database. Applying all migrations...")
            command.upgrade(alembic_cfg, "head")
            logger.info("Successfully applied all migrations.")
        else:
            logger.info("Alembic management found. Checking for pending migrations...")

            with pg_engine.connect() as conn:
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                current_revision = result.scalar()

            script = ScriptDirectory.from_config(alembic_cfg)
            head_revision = script.get_current_head()

            if current_revision != head_revision:
                logger.info(
                    f"Pending migrations detected. Current: {current_revision}, "
                    f"Target: {head_revision}. Upgrading..."
                )
                command.upgrade(alembic_cfg, "head")
                logger.info("Successfully applied pending migrations.")
            else:
                logger.info("Database is up to date. No migrations needed.")
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred while managing Alembic migrations."
        )
        raise
