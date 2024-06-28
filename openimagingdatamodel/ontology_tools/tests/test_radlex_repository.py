import os
from pathlib import Path

import pytest
import pytest_asyncio
from dotenv import dotenv_values
from motor.motor_asyncio import AsyncIOMotorClient
from openai import AsyncOpenAI, OpenAI
from openimagingdatamodel.ontology_tools.embedding_creator import (
    AsyncEmbeddingCreator,
    EmbeddingCreator,
)
from openimagingdatamodel.ontology_tools.repository import AsyncRadlexConceptRepository, RadlexConceptRepository
from pymongo import MongoClient

# Load environment variables
# Get the absolute path of the current file
current_file_path = Path(__file__).resolve()
root_dir = current_file_path.parent.parent.parent.parent
env_path = os.path.join(root_dir, ".env")
config = dotenv_values(env_path)


# Database client fixture
@pytest.fixture(scope="module")
def mongo_client():
    client = MongoClient(config["ATLAS_DSN"])
    yield client
    client.close()


# Async database client fixture
@pytest_asyncio.fixture
async def async_mongo_client():
    client = AsyncIOMotorClient(config["ATLAS_DSN"])
    yield client
    client.close()


# Test RadlexConceptRepository class methods
def test_repository_get_count(mongo_client):
    db = mongo_client["ontologies"]
    collection = db["radlex"]
    repo = RadlexConceptRepository(collection)
    count = repo.get_count()
    assert isinstance(count, int), "The count must be an integer"
    assert count > 0, "The count must be greater than zero"


@pytest.mark.parametrize("concept_id, expected", [("RID56", True), ("RID1302", True)])
def test_repository_get_concept(mongo_client, concept_id, expected):
    db = mongo_client["ontologies"]
    collection = db["radlex"]
    repo = RadlexConceptRepository(collection)
    concept = repo.get_concept(concept_id)
    assert (concept is not None) == expected, f"Concept {concept_id} existence should be {expected}"


@pytest.mark.parametrize(
    "concept_ids, expected_length",
    [
        (["RID56", "RID1302"], 2),
        ([], 0),  # Assuming no IDs returns an empty list
        (["RID56"], 1),
    ],
)
def test_repository_get_concepts(mongo_client, concept_ids, expected_length):
    db = mongo_client["ontologies"]
    collection = db["radlex"]
    repo = RadlexConceptRepository(collection)
    concepts = repo.get_concepts(concept_ids)
    assert len(concepts) == expected_length, "The number of concepts retrieved should match the expected length"


@pytest.mark.parametrize("count", [2, 5])  # Example values
def test_repository_get_random_concepts(mongo_client, count):
    db = mongo_client["ontologies"]
    collection = db["radlex"]
    repo = RadlexConceptRepository(collection)
    concepts = repo.get_random_concepts(count)
    assert len(concepts) == count, "The number of concepts retrieved should match the expected length"


@pytest.mark.parametrize("concept_id", ["RID56"])
def test_get_text_for_embedding(mongo_client, concept_id):
    db = mongo_client["ontologies"]
    collection = db["radlex"]
    repo = RadlexConceptRepository(collection)
    concept = repo.get_concept(concept_id)
    embedding_creator = EmbeddingCreator(OpenAI())
    text = embedding_creator.get_text_for_embedding(concept)
    assert isinstance(text, str), "The text must be a string"
    assert text == concept.text_for_embedding().replace(
        "\n", " "
    ), "The text must match the concept's text for embedding"


# Test AsyncRadlexConceptRepository class methods


@pytest.mark.asyncio
@pytest.mark.parametrize("expected", [0, 1, 100])  # Example values
async def test_async_repository_get_count(async_mongo_client, expected):
    db = async_mongo_client["ontologies"]
    collection = db["radlex"]
    repo = AsyncRadlexConceptRepository(collection)
    count = await repo.get_count()
    assert isinstance(count, int), "The count must be an integer"
    assert count > expected, f"The count must be greater than {expected}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "concept_id, expected",
    [
        ("RID56", True),
        ("RID1302", True),
        ("RID0000000", False),  # Assuming this ID does not exist
    ],
)
async def test_async_repository_get_concept(async_mongo_client, concept_id, expected):
    db = async_mongo_client["ontologies"]
    collection = db["radlex"]
    repo = AsyncRadlexConceptRepository(collection)
    concept = await repo.get_concept(concept_id)
    assert (concept is not None) == expected, f"Concept {concept_id} existence should be {expected}"


# Parametrized test for get_concepts method
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "concept_ids, expected_length",
    [
        (["RID56", "RID1302"], 2),
        ([], 0),  # Assuming no IDs returns an empty list
        (["RID56"], 1),
    ],
)
async def test_async_repository_get_concepts(async_mongo_client, concept_ids, expected_length):
    db = async_mongo_client["ontologies"]
    collection = db["radlex"]
    repo = AsyncRadlexConceptRepository(collection)
    concepts = await repo.get_concepts(concept_ids)
    assert len(concepts) == expected_length, "The number of concepts retrieved should match the expected length"


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [2, 5])  # Example values
async def test_async_repository_get_random_concepts(async_mongo_client, count):
    db = async_mongo_client["ontologies"]
    collection = db["radlex"]
    repo = AsyncRadlexConceptRepository(collection)
    concepts = await repo.get_random_concepts(count)
    assert len(concepts) == count, "The number of concepts retrieved should match the expected length"


@pytest.mark.asyncio
@pytest.mark.parametrize("concept_id", ["RID56"])
async def test_async_get_text_for_embedding(async_mongo_client, concept_id):
    db = async_mongo_client["ontologies"]
    collection = db["radlex"]
    repo = AsyncRadlexConceptRepository(collection)
    concept = await repo.get_concept(concept_id)
    embedding_creator = AsyncEmbeddingCreator(AsyncOpenAI())
    text = embedding_creator.get_text_for_embedding(concept)
    assert isinstance(text, str), "The text must be a string"
    assert text == concept.text_for_embedding().replace(
        "\n", " "
    ), "The text must match the concept's text for embedding"