from typing import Generator

from app.core.database import get_db
from sqlalchemy.orm import Session


def get_db_session() -> Generator[Session, None, None]:
    yield from get_db()