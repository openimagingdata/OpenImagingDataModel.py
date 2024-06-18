from typing import Any, Mapping

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection as PyMongoCollection
from pymongo.collection import UpdateOne
from pymongo.results import BulkWriteResult, UpdateResult

from .search_result import SearchResult
from .snomedct_concept import SnomedCTConcept


class AbstractSnomedCTConceptRepo:
    def __init__(self):
        raise NotImplementedError

    def _text_search_pipeline(self, search_term: str, count: int) -> list[Mapping[str, Any]]:
        return [
            {"$search": {"index": "defaultText", "text": {"query": search_term, "path": {"wildcard": "*"}}}},
            {"$limit": count},
            {
                "$project": {
                    "_id": 0,
                    "system": "SNOMEDCT",
                    "code": "$conceptId",
                    "display": "$preferredTerm",
                    "score": {"$meta": "searchScore"},
                }
            },
        ]

    def _args_for_find_multiple_ids(self, concept_ids: list[str]) -> Mapping[str, Any]:
        return {"conceptId": {"$in": concept_ids}}

    def _args_for_get_sample(self, count: int) -> list[Mapping[str, Any]]:
        return [{"$sample": {"size": count}}]

    def _process_find_results(self, raw_results) -> list[SnomedCTConcept]:
        return [SnomedCTConcept.model_validate(result) for result in raw_results]

    def _process_text_search_results(self, raw_results) -> list[SearchResult]:
        return [SearchResult.model_validate(result) for result in raw_results]

    def _embedding_vector_update_args(self, concept: SnomedCTConcept, vector: list[float]) -> tuple[dict, dict]:
        return ({"conceptId": concept.concept_id}, {"$set": {"embedding_vector": vector}})

    def _manage_vector_write_update_result(
        self, result: UpdateResult, concept: SnomedCTConcept, vector: list[float]
    ) -> bool:
        if result.modified_count == 1:
            concept.embedding_vector = vector
            return True
        return False

    def _update_commands_to_write_embedding_vectors(
        self, concepts: list[SnomedCTConcept], vectors: list[list[float]]
    ) -> list[dict]:
        return [
            UpdateOne({"_id": concept.concept_id}, {"$set": {"embedding_vector": vector}})
            for concept, vector in zip(concepts, vectors)
        ]

    def _manage_bulk_write_result(
        self, result: BulkWriteResult, concepts: list[SnomedCTConcept], vectors: list[list[float]]
    ) -> bool:
        if result.modified_count == len(concepts):
            for concept, vector in zip(concepts, vectors):
                concept.embedding_vector = vector
            return True
        return False

class AsyncSnomedCTConceptRepo(AbstractSnomedCTConceptRepo):
    def __init__(self, collection: AsyncIOMotorCollection):
        # Check to make sure we have a valid collection
        if not isinstance(collection, AsyncIOMotorCollection):
            raise ValueError("AsyncIOMotorCollection is required")
        self.collection = collection

    async def get_concept(self, concept_id: str) -> SnomedCTConcept:
        raw_concept = await self.collection.find_one({"conceptId": concept_id})
        return SnomedCTConcept.model_validate(raw_concept)

    async def get_concepts(self, concept_ids: list[str]) -> list[SnomedCTConcept]:
        args = self._args_for_find_multiple_ids(concept_ids)
        raw_results = await self.collection.find(args).to_list(len(concept_ids))
        return self._process_find_results(raw_results)

    async def get_random_concepts(self, count: int) -> list[SnomedCTConcept]:
        args = self._args_for_get_sample(count)
        raw_results = await self.collection.aggregate(args).to_list(count)
        return self._process_find_results(raw_results)

    # - Get count of all concepts
    async def get_count(self):
        return await self.collection.count_documents({})

    async def get_search_results(self, search_term: str, count: int = 50) -> list[SearchResult]:
        pipeline = self._text_search_pipeline(search_term, count)
        raw_results = await self.collection.aggregate(pipeline).to_list(count)
        return self._process_text_search_results(raw_results)

    async def write_embedding_vector(self, concept: SnomedCTConcept, vector: list[float]) -> bool:
        # Update the concept embedding vectore in the database
        args = self._embedding_vector_update_args(concept, vector)
        result = await self.collection.update_one(*args)
        return self._manage_vector_write_update_result(result, concept, vector)
    
    async def bulk_write_embedding_vectors(self, concepts: list[SnomedCTConcept], vectors: list[list[float]]) -> bool:
        update_commands = self._update_commands_to_write_embedding_vectors(concepts, vectors)
        result = await self.collection.bulk_write(update_commands)
        return self._manage_bulk_write_result(result, concepts, vectors)


class SnomedCTConceptRepo(AbstractSnomedCTConceptRepo):
    def __init__(self, collection: PyMongoCollection):
        # Check to make sure we have a valid collection
        if not isinstance(collection, PyMongoCollection):
            raise ValueError("pymongo.collection.Collection is required")
        self.collection = collection

    def get_concept(self, concept_id: str) -> SnomedCTConcept:
        concept = self.collection.find_one({"conceptId": concept_id})
        return SnomedCTConcept.model_validate(concept)

    def get_concepts(self, concept_ids: list[str]) -> list[SnomedCTConcept]:
        args = self._args_for_find_multiple_ids(concept_ids)
        raw_results = self.collection.find(args)
        return self._process_find_results(raw_results)

    def get_random_concepts(self, count: int) -> list[SnomedCTConcept]:
        args = self._args_for_get_sample(count)
        raw_results = self.collection.aggregate(args)
        return self._process_find_results(raw_results)

    def get_count(self):
        return self.collection.count_documents({})

    def get_search_results(self, search_term: str, count: int = 50) -> list[SearchResult]:
        pipeline = self._text_search_pipeline(search_term, count)
        raw_results = self.collection.aggregate(pipeline)
        return self._process_text_search_results(raw_results)

    def write_embedding_vector(self, concept: SnomedCTConcept, vector: list[float]) -> bool:
        # Update the concept embedding vectore in the database
        args = self._embedding_vector_update_args(concept, vector)
        result = self.collection.update_one(*args)
        return self._manage_vector_write_update_result(result, concept, vector)
    
    def bulk_write_embedding_vectors(self, concepts: list[SnomedCTConcept], vectors: list[list[float]]) -> bool:
        update_commands = self._update_commands_to_write_embedding_vectors(concepts, vectors)
        result = self.collection.bulk_write(update_commands)
        return self._manage_bulk_write_result(result, concepts, vectors)

    # - Write vectors back to the database for a batch of concepts
    # - Define a vector index
    # - Do a vector search
