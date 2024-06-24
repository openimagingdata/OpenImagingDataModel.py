import os
from pathlib import Path
import pytest
from pymongo import MongoClient
from dotenv import dotenv_values
from motor.motor_asyncio import AsyncIOMotorClient
import pytest_asyncio

from openimagingdatamodel.ontology_tools.repository import (
    RadlexConceptRepository,
    AsyncRadlexConceptRepository
)

# Load environment variables
# Get the absolute path of the current file
current_file_path = Path(__file__).resolve()
root_dir = current_file_path.parent.parent.parent.parent 
env_path = os.path.join(root_dir, ".env")
config = dotenv_values(env_path)

# Database client fixture
@pytest.fixture(scope='module')
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

@pytest.mark.parametrize("concept_id, expected", [
    ("RID56", True),
    ("RID1302", True)
])
def test_repository_get_concept(mongo_client, concept_id, expected):
    db = mongo_client["ontologies"]
    collection = db["radlex"]
    repo = RadlexConceptRepository(collection)
    concept = repo.get_concept(concept_id)
    assert (concept is not None) == expected, f"Concept {concept_id} existence should be {expected}"

@pytest.mark.parametrize("concept_ids, expected_length", [
    (["RID56", "RID1302"], 2),
    ([], 0),  # Assuming no IDs returns an empty list
    (["RID56"], 1)
])
def test_async_repository_get_concepts(mongo_client, concept_ids, expected_length):
    db = async_mongo_client["ontologies"]
    collection = db["radlex"]
    repo = RadlexConceptRepository(collection)
    concepts = repo.get_concepts(concept_ids)
    assert len(concepts) == expected_length, "The number of concepts retrieved should match the expected length"


# Test AsyncRadlexConceptRepository class methods
# Parametrized test for get_count method
@pytest.mark.asyncio
@pytest.mark.parametrize("expected", [0, 1, 100])  # Example values
async def test_async_repository_get_count(async_mongo_client, expected):
    db = async_mongo_client["ontologies"]
    collection = db["radlex"]
    repo = AsyncRadlexConceptRepository(collection)
    count = await repo.get_count()
    assert isinstance(count, int), "The count must be an integer"
    assert count > expected, f"The count must be greater than {expected}"

# Parametrized test for get_concept method
@pytest.mark.asyncio
@pytest.mark.parametrize("concept_id, expected", [
    ("RID56", True),
    ("RID1302", True),
    ("RID0000000", False)  # Assuming this ID does not exist
])
async def test_async_repository_get_concept(async_mongo_client, concept_id, expected):
    db = async_mongo_client["ontologies"]
    collection = db["radlex"]
    repo = AsyncRadlexConceptRepository(collection)
    concept = await repo.get_concept(concept_id)
    assert (concept is not None) == expected, f"Concept {concept_id} existence should be {expected}"

# Parametrized test for get_concepts method
@pytest.mark.asyncio
@pytest.mark.parametrize("concept_ids, expected_length", [
    (["RID56", "RID1302"], 2),
    ([], 0),  # Assuming no IDs returns an empty list
    (["RID56"], 1)
])
async def test_async_repository_get_concepts(async_mongo_client, concept_ids, expected_length):
    db = async_mongo_client["ontologies"]
    collection = db["radlex"]
    repo = AsyncRadlexConceptRepository(collection)
    concepts = await repo.get_concepts(concept_ids)
    assert len(concepts) == expected_length, "The number of concepts retrieved should match the expected length"
