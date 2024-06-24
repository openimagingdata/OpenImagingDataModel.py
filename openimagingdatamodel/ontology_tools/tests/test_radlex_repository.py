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

# Test Radlex Repository class methods
def test_repository_get_count():
    client = MongoClient(config["ATLAS_DSN"])
    db = client["ontologies"]
    collection = db["radlex"]
    repo = RadlexConceptRepository(collection)
    count = repo.get_count()
    assert isinstance(count, int)

def test_repository_get_concept():
    client = MongoClient(config["ATLAS_DSN"])
    db = client["ontologies"]
    collection = db["radlex"]
    repo = RadlexConceptRepository(collection)
    concept = repo.get_concept("RID56")
    assert concept is not None

def test_repository_get_concepts():
    client = MongoClient(config["ATLAS_DSN"])
    db = client["ontologies"]
    collection = db["radlex"]
    repo = RadlexConceptRepository(collection)
    concept_ids = ["RID56", "RID1302"]
    concepts = repo.get_concepts(concept_ids)
    assert len(concepts) == len(concept_ids)

# Test AsyncRadlexRepository class methods
@pytest.mark.asyncio
async def test_async_repository_get_count():
    client = AsyncIOMotorClient(config["ATLAS_DSN"])
    db = client["ontologies"]
    collection = db["radlex"]
    repo = AsyncRadlexConceptRepository(collection)
    count = await repo.get_count()
    assert isinstance(count, int)
    assert count > 0

@pytest.mark.asyncio
async def test_async_repository_get_concept():
    client = AsyncIOMotorClient(config["ATLAS_DSN"])
    db = client["ontologies"]
    collection = db["radlex"]
    repo = AsyncRadlexConceptRepository(collection)
    concept = await repo.get_concept("RID56")
    assert concept is not None

@pytest.mark.asyncio
async def test_async_repository_get_concepts():
    client = AsyncIOMotorClient(config["ATLAS_DSN"])
    db = client["ontologies"]
    collection = db["radlex"]
    repo = AsyncRadlexConceptRepository(collection)
    concept_ids = ["RID56", "RID1302"]
    concepts = await repo.get_concepts(concept_ids)
    assert len(concepts) == len(concept_ids)