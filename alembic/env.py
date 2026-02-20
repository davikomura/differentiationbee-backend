# alembic/env.py
from __future__ import with_statement

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.settings import get_settings
from app.db.base import Base
from app.modules.attempts.models import Attempt
from app.modules.auth.models import RefreshToken
from app.modules.game.models import IssuedQuestion
from app.modules.seasons.models import Season, SeasonTranslation
from app.modules.sessions.models import GameSession
from app.modules.tiers.models import Tier, TierTranslation
from app.modules.users.models import User

# Keep imported model symbols referenced so linters do not remove imports
_ = (Attempt, RefreshToken, IssuedQuestion, Season, SeasonTranslation, GameSession, Tier, TierTranslation, User)

config = context.config
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
