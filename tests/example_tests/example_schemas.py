import enum

from sqlalchemy import (
    BigInteger,
    Enum,
    ForeignKey,
    Identity,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)


def get_session(db_url: str = "somewhere:///overtherainbow") -> "Session":
    return Session(bind=create_engine(db_url))


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


def query_humans() -> list[Human]:
    with get_session() as session:
        return session.query(Human).all()


def query_pets() -> list[Pet]:
    with get_session() as session:
        return session.query(Pet).all()


def query_soulmates() -> list[Soulmates]:
    with get_session() as session:
        return session.query(Soulmates).join(Human).join(Pet).all()
