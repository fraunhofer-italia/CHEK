
from logging.config import fileConfig
from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool
from alembic import context
import os
from database import Base, SQLALCHEMY_DATABASE_URL
from api.models import models

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata
SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata,
        literal_binds=True, dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()
def run_migrations_online() -> None:
    url = SQLALCHEMY_DATABASE_URL or config.get_main_option("sqlalchemy.url")
    connectable = create_engine(url)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
