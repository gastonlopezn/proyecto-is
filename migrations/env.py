from logging.config import fileConfig

from alembic import context

import myapp.models  # noqa: F401
from myapp import create_app
from myapp.extensions import db

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

app = create_app()
target_metadata = db.metadata


def run_migrations_offline() -> None:
    with app.app_context():
        url = db.engine.url.render_as_string(hide_password=False)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with app.app_context(), db.engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()