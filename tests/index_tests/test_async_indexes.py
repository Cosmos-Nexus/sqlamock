from typing import TYPE_CHECKING

import pytest
from sqlalchemy import inspect

from tests.index_tests.index_schemas import Product, User

if TYPE_CHECKING:
    from sqlamock.async_connection_provider import MockAsyncConnectionProvider
    from sqlamock.async_db_mock import AsyncDBMock


@pytest.mark.asyncio
async def test_indexes_are_created(
    db_mock_async: "AsyncDBMock",
    db_mock_async_connection: "MockAsyncConnectionProvider",
):
    async with db_mock_async.from_orm(
        [User(email="test@example.com", username="testuser")]
    ):
        engine = db_mock_async_connection.get_async_engine()
        async with engine.connect() as conn:
            inspection = await conn.run_sync(inspect)

            indexes = await conn.run_sync(
                lambda sync_conn: inspection.get_indexes("user")
            )
            index_names = [idx["name"] for idx in indexes]

            assert "idx_username" in index_names


@pytest.mark.asyncio
async def test_unique_constraint_enforced(db_mock_async: "AsyncDBMock"):
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        async with db_mock_async.from_orm(
            [
                User(email="test@example.com", username="user1"),
                User(email="test@example.com", username="user2"),
            ]
        ):
            pass


@pytest.mark.asyncio
async def test_unique_constraint_on_column_enforced(db_mock_async: "AsyncDBMock"):
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        async with db_mock_async.from_orm(
            [
                Product(name="Product 1", sku="SKU001", price=100),
                Product(name="Product 2", sku="SKU001", price=200),
            ]
        ):
            pass


@pytest.mark.asyncio
async def test_composite_unique_constraint_enforced(db_mock_async: "AsyncDBMock"):
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        async with db_mock_async.from_orm(
            [
                User(email="test@example.com", username="testuser"),
                User(email="test@example.com", username="testuser"),
            ]
        ):
            pass
    async with db_mock_async.from_orm(
        [
            User(email="test1@example.com", username="user1"),
            User(email="test2@example.com", username="user2"),
        ]
    ):
        pass


@pytest.mark.asyncio
async def test_indexes_exist_on_product_table(
    db_mock_async: "AsyncDBMock",
    db_mock_async_connection: "MockAsyncConnectionProvider",
):
    async with db_mock_async.from_orm(
        [Product(name="Test Product", sku="SKU001", price=100)]
    ):
        engine = db_mock_async_connection.get_async_engine()
        async with engine.connect() as conn:
            inspection = await conn.run_sync(inspect)

            indexes = await conn.run_sync(
                lambda sync_conn: inspection.get_indexes("product")
            )
            index_names = [idx["name"] for idx in indexes]

            assert "idx_product_name" in index_names


@pytest.mark.asyncio
async def test_partial_index_created(
    db_mock_async: "AsyncDBMock",
    db_mock_async_connection: "MockAsyncConnectionProvider",
):
    async with db_mock_async.from_orm(
        [
            User(email="active@example.com", username="active", active=True),
            User(email="inactive@example.com", username="inactive", active=False),
        ]
    ):
        engine = db_mock_async_connection.get_async_engine()
        async with engine.connect() as conn:
            inspection = await conn.run_sync(inspect)

            indexes = await conn.run_sync(
                lambda sync_conn: inspection.get_indexes("user")
            )
            index_names = [idx["name"] for idx in indexes]

            assert "idx_active_users" in index_names or any(
                "idx_active_users" in idx.get("name", "") for idx in indexes
            )


@pytest.mark.asyncio
async def test_partial_index_on_product(
    db_mock_async: "AsyncDBMock",
    db_mock_async_connection: "MockAsyncConnectionProvider",
):
    async with db_mock_async.from_orm(
        [
            Product(name="Active Product", sku="SKU001", price=100, archived=False),
            Product(name="Archived Product", sku="SKU002", price=200, archived=True),
        ]
    ):
        engine = db_mock_async_connection.get_async_engine()
        async with engine.connect() as conn:
            inspection = await conn.run_sync(inspect)

            indexes = await conn.run_sync(
                lambda sync_conn: inspection.get_indexes("product")
            )
            index_names = [idx["name"] for idx in indexes]

            assert "idx_active_products" in index_names or any(
                "idx_active_products" in idx.get("name", "") for idx in indexes
            )


@pytest.mark.asyncio
async def test_multiple_indexes_on_same_table(
    db_mock_async: "AsyncDBMock",
    db_mock_async_connection: "MockAsyncConnectionProvider",
):
    async with db_mock_async.from_orm(
        [
            User(email="user1@example.com", username="user1", active=True),
            User(email="user2@example.com", username="user2", active=False),
        ]
    ):
        engine = db_mock_async_connection.get_async_engine()
        async with engine.connect() as conn:
            inspection = await conn.run_sync(inspect)

            indexes = await conn.run_sync(
                lambda sync_conn: inspection.get_indexes("user")
            )
            index_names = [idx["name"] for idx in indexes]

            assert (
                len(
                    [
                        name
                        for name in index_names
                        if name in ("idx_username", "idx_active_users")
                    ]
                )
                >= 1
            )


@pytest.mark.asyncio
async def test_index_idempotency(
    db_mock_async: "AsyncDBMock",
    db_mock_async_connection: "MockAsyncConnectionProvider",
):
    """Test that indexes are created correctly even when table already exists."""
    # First context: create table with indexes
    async with db_mock_async.from_orm(
        [User(email="user1@example.com", username="user1")]
    ):
        engine = db_mock_async_connection.get_async_engine()
        async with engine.connect() as conn:
            inspection = await conn.run_sync(inspect)

            indexes = await conn.run_sync(
                lambda sync_conn: inspection.get_indexes("user")
            )
            index_names = [idx["name"] for idx in indexes]
            assert "idx_username" in index_names

    # Second context: table already exists, should handle gracefully
    async with db_mock_async.from_orm(
        [User(email="user2@example.com", username="user2")]
    ):
        engine = db_mock_async_connection.get_async_engine()
        async with engine.connect() as conn:
            inspection = await conn.run_sync(inspect)

            # Indexes should still exist
            indexes = await conn.run_sync(
                lambda sync_conn: inspection.get_indexes("user")
            )
            index_names = [idx["name"] for idx in indexes]
            assert "idx_username" in index_names


@pytest.mark.asyncio
async def test_multi_column_partial_index(
    db_mock_async: "AsyncDBMock",
    db_mock_async_connection: "MockAsyncConnectionProvider",
):
    """Test that multi-column partial indexes are created correctly."""
    async with db_mock_async.from_orm(
        [
            Product(name="Active Product 1", sku="SKU001", price=100, archived=False),
            Product(name="Active Product 2", sku="SKU002", price=200, archived=False),
            Product(name="Archived Product", sku="SKU003", price=150, archived=True),
        ]
    ):
        engine = db_mock_async_connection.get_async_engine()
        async with engine.connect() as conn:
            inspection = await conn.run_sync(inspect)

            indexes = await conn.run_sync(
                lambda sync_conn: inspection.get_indexes("product")
            )
            index_names = [idx["name"] for idx in indexes]

            # Verify the multi-column partial index exists
            assert "idx_active_products" in index_names or any(
                "idx_active_products" in idx.get("name", "") for idx in indexes
            )

            # Find the specific index and verify it has multiple columns
            active_products_idx = next(
                (idx for idx in indexes if idx.get("name") == "idx_active_products"),
                None,
            )
            if active_products_idx:
                # The index should have both 'name' and 'price' columns
                assert len(active_products_idx.get("column_names", [])) == 2


@pytest.mark.asyncio
async def test_index_without_postgresql_where(
    db_mock_async: "AsyncDBMock",
    db_mock_async_connection: "MockAsyncConnectionProvider",
):
    """Test that indexes without postgresql_where are created normally."""
    async with db_mock_async.from_orm(
        [Product(name="Test Product", sku="SKU001", price=100)]
    ):
        engine = db_mock_async_connection.get_async_engine()
        async with engine.connect() as conn:
            inspection = await conn.run_sync(inspect)

            indexes = await conn.run_sync(
                lambda sync_conn: inspection.get_indexes("product")
            )
            index_names = [idx["name"] for idx in indexes]

            # idx_product_name doesn't have postgresql_where, should be created normally
            assert "idx_product_name" in index_names
