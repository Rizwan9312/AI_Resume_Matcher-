"""Quick script to check database state."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check():
    engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/resume_matcher")
    async with engine.begin() as conn:
        # Check existing enum values
        result = await conn.execute(text(
            "SELECT enumlabel FROM pg_enum e "
            "JOIN pg_type t ON e.enumtypid = t.oid "
            "WHERE t.typname = 'plan_type'"
        ))
        rows = result.fetchall()
        print("plan_type enum values:", [r[0] for r in rows])

        # Check all enums
        result = await conn.execute(text(
            "SELECT t.typname, e.enumlabel FROM pg_enum e "
            "JOIN pg_type t ON e.enumtypid = t.oid "
            "ORDER BY t.typname, e.enumsortorder"
        ))
        rows = result.fetchall()
        print("All enum values:")
        for r in rows:
            print(f"  {r[0]}: {r[1]}")

        # Check existing tables
        result = await conn.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        ))
        rows = result.fetchall()
        print("Existing tables:", [r[0] for r in rows])
    await engine.dispose()

asyncio.run(check())
