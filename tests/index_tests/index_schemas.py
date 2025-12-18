from sqlalchemy import (
    BigInteger,
    Boolean,
    Identity,
    Index,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
    text,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class IndexBase(DeclarativeBase):
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)


def get_index_session(db_url: str = "somewhere:///overtherainbow") -> "Session":
    return Session(bind=create_engine(db_url))


async def get_index_async_session(
    db_url: str = "somewhere:///overtherainbow",
) -> "AsyncSession":
    engine = create_async_engine(db_url)
    return AsyncSession(bind=engine)


class User(IndexBase):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(String, unique=True)
    username: Mapped[str] = mapped_column(String)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        Index("idx_username", "username"),
        Index("idx_active_users", "active", postgresql_where=text("active = true")),
        UniqueConstraint("username", "email", name="uq_username_email"),
    )


class Product(IndexBase):
    __tablename__ = "product"

    name: Mapped[str] = mapped_column(String)
    sku: Mapped[str] = mapped_column(String, unique=True)
    price: Mapped[int] = mapped_column(Integer)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        Index("idx_product_name", "name"),
        Index(
            "idx_active_products",
            "name",
            "price",
            postgresql_where=text("archived = false"),
        ),
    )


class OrderItem(IndexBase):
    __tablename__ = "order_item"

    id: Mapped[int | None] = mapped_column(BigInteger, primary_key=False, default=None)
    order_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[int] = mapped_column(Integer)
