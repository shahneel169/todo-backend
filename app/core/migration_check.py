import logging

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from app.core.database import engine

logger = logging.getLogger(__name__)


def check_migrations():
    """Check if there are pending migrations."""
    try:
        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)

        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
            head_rev = script.get_current_head()

            if current_rev != head_rev:
                message = (
                    f"⚠️  Database is not up to date! "
                    f"Current: {current_rev}, Head: {head_rev}. "
                    f"Run 'alembic upgrade head' to apply pending migrations."
                )
                logger.warning(message)
                print(message)  # Also print to console
                return False
            else:
                message = "✅ Database migrations are up to date."
                logger.info(message)
                print(message)  # Also print to console
                return True
    except Exception as e:
        logger.error(f"Error checking migrations: {e}")
        return None
        return None
