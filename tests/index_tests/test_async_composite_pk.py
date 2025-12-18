from typing import TYPE_CHECKING

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError

from tests.index_tests.index_schemas import IndexBase, OrderItem, User

if TYPE_CHECKING:
    from sqlamock.async_connection_provider import MockAsyncConnectionProvider
    from sqlamock.async_db_mock import AsyncDBMock


@pytest.mark.asyncio
async def test_composite_pk_no_autoincrement(
    db_mock_async: "AsyncDBMock",
    db_mock_async_connection: "MockAsyncConnectionProvider",
):
    async with db_mock_async.from_orm(
        [
            OrderItem(order_id=1, item_id=1, quantity=5, price=100),
            OrderItem(order_id=1, item_id=2, quantity=3, price=200),
            OrderItem(order_id=2, item_id=1, quantity=2, price=150),
        ]
    ):
        engine = db_mock_async_connection.get_async_engine()
        async with engine.connect() as conn:
            inspection = await conn.run_sync(inspect)

            has_table = await conn.run_sync(
                lambda sync_conn: inspection.has_table("order_item")
            )
            assert has_table

        async with db_mock_async_connection.get_async_session() as session:
            result = await session.execute(select(OrderItem))
            items = list(result.scalars().all())
            assert len(items) == 3
            assert items[0].order_id == 1
            assert items[0].item_id == 1


@pytest.mark.asyncio
async def test_single_pk_has_autoincrement(
    db_mock_async: "AsyncDBMock",
    db_mock_async_connection: "MockAsyncConnectionProvider",
):
    async with db_mock_async.from_orm(
        [User(email="test@example.com", username="testuser")]
    ):
        async with db_mock_async_connection.get_async_session() as session:
            result = await session.execute(select(User))
            user = result.scalar_one_or_none()
            assert user is not None
            assert user.id == 1


@pytest.mark.asyncio
async def test_composite_pk_uniqueness_enforced(db_mock_async: "AsyncDBMock"):
    with pytest.raises(IntegrityError):
        async with db_mock_async.from_orm(
            [
                OrderItem(order_id=1, item_id=1, quantity=5, price=100),
                OrderItem(order_id=1, item_id=1, quantity=3, price=200),
            ]
        ):
            pass


@pytest.mark.asyncio
async def test_composite_pk_partial_uniqueness_allowed(db_mock_async: "AsyncDBMock"):
    async with db_mock_async.from_orm(
        [
            OrderItem(order_id=1, item_id=1, quantity=5, price=100),
            OrderItem(order_id=1, item_id=2, quantity=3, price=200),
            OrderItem(order_id=2, item_id=1, quantity=2, price=150),
        ]
    ):
        pass

