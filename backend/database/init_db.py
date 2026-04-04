"""
Database initialisation: create all tables and seed default admin user.
"""

from passlib.context import CryptContext
from sqlalchemy import select

from database.engine import Base, engine, async_session_factory

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def init_db() -> None:
    """Create tables and seed the default admin user."""
    # Import models so Base.metadata knows about them
    from models.telemetry import TelemetryReading, AlertEvent  # noqa: F401
    from models.user import User  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default admin
    from config import get_settings
    settings = get_settings()

    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.username == settings.DEFAULT_ADMIN_USERNAME)
        )
        if result.scalar_one_or_none() is None:
            admin = User(
                username=settings.DEFAULT_ADMIN_USERNAME,
                hashed_password=pwd_context.hash(settings.DEFAULT_ADMIN_PASSWORD),
                role="admin",
                is_active=True,
            )
            session.add(admin)
            await session.commit()
