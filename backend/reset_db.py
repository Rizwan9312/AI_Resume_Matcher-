"""Reset database and create all tables properly."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def reset():
    engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/resume_matcher")
    async with engine.begin() as conn:
        # Drop all tables and types  
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        print("Schema reset complete.")
    await engine.dispose()

asyncio.run(reset())
