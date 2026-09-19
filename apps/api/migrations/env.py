import os

from alembic import context
from sqlalchemy import create_engine, pool

# Migration credentials are never taken from the application's runtime URL.
url = os.environ["MIGRATION_DATABASE_URL"]
if context.is_offline_mode():
    context.configure(url=url, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(url, poolclass=pool.NullPool, hide_parameters=True)
    with engine.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()
