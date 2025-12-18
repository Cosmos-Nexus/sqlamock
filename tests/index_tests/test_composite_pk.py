from typing import TYPE_CHECKING

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from tests.index_tests.index_schemas import IndexBase, OrderItem, User

if TYPE_CHECKING:
    from sqlamock.connection_provider import MockConnectionProvider
    from sqlamock.db_mock import DBMock


def test_composite_pk_no_autoincrement(
    db_mock: "DBMock", db_mock_connection: "MockConnectionProvider"
):
    with db_mock.from_orm(
        [
            OrderItem(order_id=1, item_id=1, quantity=5, price=100),
            OrderItem(order_id=1, item_id=2, quantity=3, price=200),
            OrderItem(order_id=2, item_id=1, quantity=2, price=150),
        ]
    ):
        engine = db_mock_connection.get_engine()
        inspection = inspect(engine)

        assert inspection.has_table("order_item")

        with db_mock_connection.get_session() as session:
            items = session.query(OrderItem).all()
            assert len(items) == 3
            assert items[0].order_id == 1
            assert items[0].item_id == 1


def test_single_pk_has_autoincrement(
    db_mock: "DBMock", db_mock_connection: "MockConnectionProvider"
):
    with db_mock.from_orm([User(email="test@example.com", username="testuser")]):
        engine = db_mock_connection.get_engine()

        with db_mock_connection.get_session() as session:
            user = session.query(User).first()
            assert user is not None
            assert user.id == 1


def test_composite_pk_uniqueness_enforced(db_mock: "DBMock"):
    with pytest.raises(IntegrityError):
        with db_mock.from_orm(
            [
                OrderItem(order_id=1, item_id=1, quantity=5, price=100),
                OrderItem(order_id=1, item_id=1, quantity=3, price=200),
            ]
        ):
            pass


def test_composite_pk_partial_uniqueness_allowed(db_mock: "DBMock"):
    with db_mock.from_orm(
        [
            OrderItem(order_id=1, item_id=1, quantity=5, price=100),
            OrderItem(order_id=1, item_id=2, quantity=3, price=200),
            OrderItem(order_id=2, item_id=1, quantity=2, price=150),
        ]
    ):
        pass

