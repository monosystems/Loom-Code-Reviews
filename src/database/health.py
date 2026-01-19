from sqlalchemy import text

from src.database.connection import engine


async def check_database_connection() -> dict:
    """Check if database connection is working."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
            return {
                "status": "healthy",
                "message": "Database connection successful"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": str(e)
        }


async def get_database_version() -> dict:
    """Get PostgreSQL version."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            row = result.fetchone()
            return {
                "status": "ok",
                "version": row[0] if row else "unknown"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
