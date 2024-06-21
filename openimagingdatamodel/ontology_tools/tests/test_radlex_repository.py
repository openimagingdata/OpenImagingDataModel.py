
import pytest
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import pytest_asyncio

from openimagingdatamodel.ontology_tools.repository import (
    RadlexConceptRepository,
    AsyncRadlexConceptRepository
)

# Test Radlex Repository class methods
def test_repository_get_count():
    client = MongoClient()
    db = client["ontologies"]
    collection = db["radlex"]
    repo = RadlexConceptRepository(collection)
    count = repo.get_count()
    assert isinstance(count, int)

def test_repository_get_concept():
    client = MongoClient()
    db = client["ontologies"]
    collection = db["radlex"]
    repo = RadlexConceptRepository(collection)
    concept = repo.get_concept("RID56")
    assert concept is not None

def test_repository_get_concepts():
    client = MongoClient()
    db = client["ontologies"]
    collection = db["radlex"]
    repo = RadlexConceptRepository(collection)
    concept_ids = ["RID56", "RID1302"]
    concepts = repo.get_concepts(concept_ids)
    assert len(concepts) == len(concept_ids)

# Test AsyncRadlexRepository class methods
@pytest.mark.asyncio
async def test_async_repository_get_count():
    client = AsyncIOMotorClient()
    db = client["ontologies"]
    collection = db["radlex"]
    repo = AsyncRadlexConceptRepository(collection)
    count = await repo.get_count()
    assert isinstance(count, int)

@pytest.mark.asyncio
async def test_async_repository_get_concept():
    client = AsyncIOMotorClient()
    db = client["ontologies"]
    collection = db["radlex"]
    repo = AsyncRadlexConceptRepository(collection)
    concept = await repo.get_concept("RID56")
    assert concept is not None

@pytest.mark.asyncio
async def test_async_repository_get_concepts():
    client = AsyncIOMotorClient()
    db = client["ontologies"]
    collection = db["radlex"]
    repo = AsyncRadlexConceptRepository(collection)
    concept_ids = ["RID56", "RID1302"]
    concepts = await repo.get_concepts(concept_ids)
    assert len(concepts) == len(concept_ids)