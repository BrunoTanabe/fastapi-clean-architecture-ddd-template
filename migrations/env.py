from logging.config import fileConfig

from alembic import context

from app.core.database import pg_engine
from app.modules.authentication.infrastructure.models import (
    SessionModel,
    AccessTokenModel,
    RefreshTokenModel,
)
from app.modules.health.infrastructure.models import AlembicModel
from app.modules.shared.infrastructure.models import Base
from app.modules.user.infrastructure.models import UserModel


_ = [
    AccessTokenModel,
    AlembicModel,
    RefreshTokenModel,
    SessionModel,
    UserModel,
]

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = pg_engine.url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with pg_engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
