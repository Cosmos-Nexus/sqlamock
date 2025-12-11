from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError

from tests.example_tests.example_schemas import (
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
    from sqlamock.connection_provider import MockConnectionProvider
    from sqlamock.db_mock import DBMock


def test_invalid_mock_data(db_mock: "DBMock"):
    with pytest.raises(IntegrityError):
        with db_mock.from_dict({"pet": [{"name": "Milo"}]}):
            pass


def test_invalid_mock_data_enums(db_mock: "DBMock"):
    with pytest.raises(IntegrityError):
        with db_mock.from_dict({"pet": [{"name": "Milo", "species": "doggy"}]}):
            pass


def test_enum_encoding(db_mock: "DBMock"):
    with db_mock.from_dict(
        {"pet": [{"name": "Milo", "species": "DOG"}]}
    ) as mocked_data:
        assert mocked_data["pet"][0].species is Species.DOG


def test_simple_mock_from_orm(db_mock: "DBMock"):
    with db_mock.from_orm(
        [Human(name="John"), Pet(name="Milo", species=Species.DOG)]
    ) as mocked_data:
        assert mocked_data[Human][0].name == "John"
        assert mocked_data["pet"][0].name == "Milo"
        # Test Querying Soulmates with Human + Pet - should exist
        humans = query_humans()
        assert len(humans) == 1
        assert humans[0].name == "John"

        pets = query_pets()
        assert len(pets) == 1
        assert pets[0].name == "Milo"

    # Test Querying Soulmates with Human + Pet - should not exist
    humans = query_humans()
    assert len(humans) == 0

    pets = query_pets()
    assert len(pets) == 0


def test_relationship_mock_from_orm(db_mock: "DBMock"):
    with db_mock.from_orm(
        [
            Human(id=1, name="John"),
            Pet(id=1, name="Milo", species=Species.DOG),
            Soulmates(human_id=1, pet_id=1),
        ]
    ):
        # Test Querying Soulmates with Human + Pet - should exist
        soul_mate = query_soulmates()
        assert len(query_soulmates()) == 1
        assert soul_mate[0].human.id == 1
        assert soul_mate[0].pet.id == 1

    # Test Querying Soulmates with Human + Pet - should not exist
    assert len(query_soulmates()) == 0


def test_nested_db_mock_contexts(db_mock: "DBMock"):
    with db_mock.from_orm(
        [Human(name="John"), Pet(name="Milo", species=Species.DOG)]
    ) as mocked_data:
        assert mocked_data["human"][0].name == "John"
        assert mocked_data["pet"][0].name == "Milo"

        assert len(query_humans()) == 1
        assert len(query_pets()) == 1

        with db_mock.from_orm(
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
            assert len(query_soulmates()) == 1
            assert query_soulmates()[0].human.id == 1
            assert query_soulmates()[0].pet.id == 1

        # Test Querying Soulates - shouldn't exist
        assert len(query_soulmates()) == 0
        assert len(query_humans()) == 1
        assert len(query_pets()) == 1


def test_db_mock_from_dict(db_mock: "DBMock"):
    with db_mock.from_dict(
        {"human": [{"name": "John"}], "pet": [{"name": "Milo", "species": Species.DOG}]}
    ) as mocked_data:
        assert mocked_data["human"][0].name == "John"
        assert mocked_data["pet"][0].name == "Milo"
        humans = query_humans()
        assert len(humans) == 1
        assert humans[0].name == "John"
        pets = query_pets()
        assert len(pets) == 1
        assert pets[0].name == "Milo"


def test_db_mock_from_file(db_mock: "DBMock"):
    path = Path(__file__).parent.parent / "data" / "example_app.json"
    with db_mock.from_file(path) as mocked_data:
        assert mocked_data["human"][0].name == "John"
        humans = query_humans()
        assert len(humans) == 1
        assert humans[0].name == "John"

        pets = query_pets()
        assert len(pets) == 1
        assert pets[0].name == "Milo"
