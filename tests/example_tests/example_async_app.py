import enum

from sqlalchemy import (
    BigInteger,
    Enum,
    ForeignKey,
    Identity,
    Integer,
    String,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)


def get_session(db_url: str = "somewhere:///overtherainbow") -> "AsyncSession":
    raise Exception("This should not be relevant")


class Species(enum.Enum):
    DOG = "dog"
    CAT = "cat"


class Pet(Base):
    __tablename__ = "pet"

    name: Mapped[str] = mapped_column(String)
    species: Mapped[Species] = mapped_column(Enum(Species))


class Human(Base):
    __tablename__ = "human"
    name: Mapped[str] = mapped_column(String)


class Soulmates(Base):
    __tablename__ = "soulmates"

    human_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("human.id", ondelete="SET NULL")
    )
    pet_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pet.id", ondelete="SET NULL")
    )

    human: Mapped[Human] = relationship(Human, lazy="selectin")
    pet: Mapped[Pet] = relationship(Pet, lazy="selectin")


async def query_humans() -> list[Human]:
    async with get_session() as session:
        result = await session.scalars(select(Human))
        return list(result.all())


async def query_pets() -> list[Pet]:
    async with get_session() as session:
        result = await session.scalars(select(Pet))
        return list(result.all())


async def query_soulmates() -> list[Soulmates]:
    async with get_session() as session:
        result = await session.scalars(select(Soulmates).join(Human).join(Pet))
        return list(result.all())
