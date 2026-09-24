import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.core.security import get_password_hash, create_access_token
from app.models.user import User, UserRole

# Use SQLite in-memory database for rapid and isolated automated testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def buyer_user(db_session: AsyncSession) -> User:
    buyer = User(
        email="buyer_test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test Buyer",
        company_name="Buyer Enterprise Logistics",
        role=UserRole.BUYER
    )
    db_session.add(buyer)
    await db_session.commit()
    await db_session.refresh(buyer)
    return buyer


@pytest_asyncio.fixture(scope="function")
async def supplier1(db_session: AsyncSession) -> User:
    supplier = User(
        email="supplier1_test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Supplier One",
        company_name="Alpha Carriers",
        role=UserRole.SUPPLIER
    )
    db_session.add(supplier)
    await db_session.commit()
    await db_session.refresh(supplier)
    return supplier


@pytest_asyncio.fixture(scope="function")
async def supplier2(db_session: AsyncSession) -> User:
    supplier = User(
        email="supplier2_test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Supplier Two",
        company_name="Beta Freight",
        role=UserRole.SUPPLIER
    )
    db_session.add(supplier)
    await db_session.commit()
    await db_session.refresh(supplier)
    return supplier


@pytest_asyncio.fixture(scope="function")
async def supplier3(db_session: AsyncSession) -> User:
    supplier = User(
        email="supplier3_test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Supplier Three",
        company_name="Gamma Shipping",
        role=UserRole.SUPPLIER
    )
    db_session.add(supplier)
    await db_session.commit()
    await db_session.refresh(supplier)
    return supplier


def get_auth_headers(user: User) -> dict:
    token = create_access_token(subject=user.id, role=user.role.value)
    return {"Authorization": f"Bearer {token}"}
