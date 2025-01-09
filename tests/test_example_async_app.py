from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError

from .example_async_app import (
    Base,
    DeclarativeBase,
    Human,
    Pet,
    Soulmates,
    Species,
    query_humans,
    query_pets,
    query_soulmates,
)

if TYPE_CHECKING:
    from sqlamock.async_connection_provider import MockAsyncConnectionProvider
    from sqlamock.async_db_mock import AsyncDBMock


@pytest.fixture(scope="session")
def db_mock_base_model() -> "type[DeclarativeBase]":
    return Base


@pytest.fixture(scope="session", autouse=True)
def mock_session(db_mock_async_connection: "MockAsyncConnectionProvider"):
    def get_session(*args, **kwargs):
        return db_mock_async_connection.get_async_session()

    with patch("tests.example_async_app.get_session", get_session):
        yield


@pytest.mark.asyncio
async def test_invalid_mock_data(db_mock_async: "AsyncDBMock"):
    with pytest.raises(IntegrityError):
        async with db_mock_async.from_dict({"pet": [{"name": "Milo"}]}):
            pass


@pytest.mark.asyncio
async def test_invalid_mock_data_enums(db_mock_async: "AsyncDBMock"):
    with pytest.raises(IntegrityError):
        async with db_mock_async.from_dict(
            {"pet": [{"name": "Milo", "species": "doggy"}]}
        ):
            pass


@pytest.mark.asyncio
async def test_enum_encoding(db_mock_async: "AsyncDBMock"):
    async with db_mock_async.from_dict(
        {"pet": [{"name": "Milo", "species": "DOG"}]}
    ) as mocked_data:
        assert mocked_data["pet"][0].species is Species.DOG


@pytest.mark.asyncio
async def test_simple_mock_from_orm(db_mock_async: "AsyncDBMock"):
    async with db_mock_async.from_orm(
        [Human(name="John"), Pet(name="Milo", species=Species.DOG)]
    ) as mocked_data:
        assert mocked_data[Human][0].name == "John"
        assert mocked_data["pet"][0].name == "Milo"
        # Test Querying Soulmates with Human + Pet - should exist
        humans = await query_humans()
        assert len(humans) == 1
        assert humans[0].name == "John"

        pets = await query_pets()
        assert len(pets) == 1
        assert pets[0].name == "Milo"
    # Test Querying Soulmates with Human + Pet - should not exist
    humans = await query_humans()
    assert len(humans) == 0

    pets = await query_pets()
    assert len(pets) == 0


@pytest.mark.asyncio
async def test_relationship_mock_from_orm(db_mock_async: "AsyncDBMock"):
    async with db_mock_async.from_orm(
        [
            Human(id=1, name="John"),
            Pet(id=1, name="Milo", species=Species.DOG),
            Soulmates(human_id=1, pet_id=1),
        ]
    ):
        # Test Querying Soulmates with Human + Pet - should exist
        soul_mate = await query_soulmates()
        assert len(soul_mate) == 1
        assert soul_mate[0].human.id == 1
        assert soul_mate[0].pet.id == 1

    # Test Querying Soulmates with Human + Pet - should not exist
    assert len(await query_soulmates()) == 0


@pytest.mark.asyncio
async def test_nested_db_mock_contexts(db_mock_async: "AsyncDBMock"):
    async with db_mock_async.from_orm(
        [Human(name="John"), Pet(name="Milo", species=Species.DOG)]
    ) as mocked_data:
        assert mocked_data["human"][0].name == "John"
        assert mocked_data["pet"][0].name == "Milo"

        assert len(await query_humans()) == 1
        assert len(await query_pets()) == 1

        async with db_mock_async.from_orm(
            [
                Soulmates(
                    human_id=mocked_data["human"][0].id, pet_id=mocked_data["pet"][0].id
                )
            ]
        ) as nested_mocked_data:
            assert (
                nested_mocked_data["soulmates"][0].human_id
                == mocked_data["human"][0].id
            )
            assert nested_mocked_data["soulmates"][0].pet_id == mocked_data["pet"][0].id

            # Test Querying Soulmates with Human + Pet - should exist
            assert len(await query_soulmates()) == 1
            assert (await query_soulmates())[0].human.id == 1
            assert (await query_soulmates())[0].pet.id == 1

        # Test Querying Soulmates - shouldn't exist
        assert len(await query_soulmates()) == 0
        assert len(await query_humans()) == 1
        assert len(await query_pets()) == 1


@pytest.mark.asyncio
async def test_db_mock_from_dict(db_mock_async: "AsyncDBMock"):
    async with db_mock_async.from_dict(
        {"human": [{"name": "John"}], "pet": [{"name": "Milo", "species": Species.DOG}]}
    ) as mocked_data:
        assert mocked_data["human"][0].name == "John"
        assert mocked_data["pet"][0].name == "Milo"
        humans = await query_humans()
        assert len(humans) == 1
        assert humans[0].name == "John"
        pets = await query_pets()
        assert len(pets) == 1
        assert pets[0].name == "Milo"


@pytest.mark.asyncio
async def test_db_mock_from_file(db_mock_async: "AsyncDBMock"):
    path = Path(__file__).parent / "data" / "example_app.json"
    async with db_mock_async.from_file(path) as mocked_data:
        assert mocked_data["human"][0].name == "John"
        humans = await query_humans()
        assert len(humans) == 1
        assert humans[0].name == "John"

        pets = await query_pets()
        assert len(pets) == 1
        assert pets[0].name == "Milo"
