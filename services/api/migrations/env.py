"""Run reviewed PostgreSQL revisions using a deployment-only owner connection."""

import os

from alembic import context
from sqlalchemy import create_engine, pool

url = os.environ["NURSERY_MIGRATION_URL"].replace("postgresql://", "postgresql+psycopg://", 1)
engine = create_engine(url, poolclass=pool.NullPool)
with engine.connect() as connection:
    context.configure(connection=connection, transactional_ddl=True)
    with context.begin_transaction():
        context.run_migrations()
