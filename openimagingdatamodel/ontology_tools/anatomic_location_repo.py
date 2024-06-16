from typing import Any, Mapping

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection as PyMongoCollection
from pymongo.collection import UpdateOne
from pymongo.results import BulkWriteResult, UpdateResult

from .anatomic_location import AnatomicLocation
from .search_result import SearchResult


class BaseAnatomicLocationRepo:
    def __init__(self) -> None:
        raise NotImplementedError

    def _text_search_pipeline(self, search_term: str, count: int) -> list[Mapping[str, Any]]:
        return [
            {"$search": {"index": "defaultText", "text": {"query": search_term, "path": {"wildcard": "*"}}}},
            {"$limit": count},
            {
                "$project": {
                    "_id": 0,
                    "system": "ANTOMICLOCATIONS",
                    "code": "$_id",
                    "display": "$description",
                    "score": {"$meta": "searchScore"},
                }
            },
        ]

    def _args_for_find_multiple_ids(self, concept_ids: list[str]) -> Mapping[str, Any]:
        return {"_id": {"$in": concept_ids}}

    def _args_for_get_sample(self, count: int) -> list[Mapping[str, Any]]:
        return [{"$sample": {"size": count}}]

    def _process_find_results(self, raw_results) -> list[AnatomicLocation]:
        return [AnatomicLocation.model_validate(result) for result in raw_results]

    def _process_text_search_results(self, raw_results) -> list[SearchResult]:
        return [SearchResult.model_validate(result) for result in raw_results]

    def _embedding_vector_update_args(self, concept: AnatomicLocation, vector: list[float]) -> tuple[dict, dict]:
        return ({"_id": concept.id}, {"$set": {"embedding_vector": vector}})

    def _manage_vector_write_update_result(
        self, result: UpdateResult, concept: AnatomicLocation, vector: list[float]
    ) -> bool:
        if result.modified_count == 1:
            concept.embedding_vector = vector
            return True
        return False

    def _update_commands_to_write_embedding_vectors(
        self, concepts: list[AnatomicLocation], vectors: list[list[float]]
    ) -> list[dict]:
        return [
            UpdateOne({"_id": concept.id}, {"$set": {"embedding_vector": vector}})
            for concept, vector in zip(concepts, vectors)
        ]

    def _manage_bulk_write_result(
        self, result: BulkWriteResult, concepts: list[AnatomicLocation], vectors: list[list[float]]
    ) -> bool:
        if result.modified_count == len(concepts):
            for concept, vector in zip(concepts, vectors):
                concept.embedding_vector = vector
            return True
        return False


class AsyncAnatomicLocationRepo(BaseAnatomicLocationRepo):
    def __init__(self, collection: AsyncIOMotorCollection):
        if not isinstance(collection, AsyncIOMotorCollection):
            raise ValueError("AsyncIOMotorCollection is required")
        self.collection = collection

    async def get_concept(self, concept_id: str) -> AnatomicLocation:
        raw_result = await self.collection.find_one({"_id": concept_id})
        return AnatomicLocation.model_validate(raw_result)

    async def get_concepts(self, concept_ids: list[str]) -> list[AnatomicLocation]:
        raw_results = await self.collection.find(self._args_for_find_multiple_ids(concept_ids)).to_list(
            len(concept_ids)
        )
        return self._process_find_results(raw_results)

    async def text_search(self, search_term: str, count: int) -> list[SearchResult]:
        raw_results = await self.collection.aggregate(self._text_search_pipeline(search_term, count)).to_list(count)
        return self._process_text_search_results(raw_results)

    async def get_random_concepts(self, count: int) -> list[AnatomicLocation]:
        raw_results = await self.collection.aggregate(self._args_for_get_sample(count)).to_list(count)
        return self._process_find_results(raw_results)

    async def update_embedding_vector(self, concept: AnatomicLocation, vector: list[float]) -> bool:
        result = await self.collection.update_one(*self._embedding_vector_update_args(concept, vector))
        return self._manage_vector_write_update_result(result, concept, vector)

    async def get_count(self):
        return await self.collection.count_documents({})

    async def get_search_results(self, search_term: str, count: int = 50) -> list[SearchResult]:
        pipeline = self._text_search_pipeline(search_term, count)
        raw_results = await self.collection.aggregate(pipeline).to_list(count)
        return self._process_text_search_results(raw_results)

    async def write_embedding_vector(self, concept: AnatomicLocation, vector: list[float]) -> bool:
        filter_args, update_args = self._embedding_vector_update_args(concept, vector)
        result = await self.collection.update_one(filter_args, update_args)
        return self._manage_vector_write_update_result(result, concept, vector)

    async def bulk_write_embedding_vectors(self, concepts: list[AnatomicLocation], vectors: list[list[float]]) -> bool:
        update_commands = self._update_commands_to_write_embedding_vectors(concepts, vectors)
        result = await self.collection.bulk_write(update_commands)
        return self._manage_bulk_write_result(result, concepts, vectors)


class AnatomicLocationRepo(BaseAnatomicLocationRepo):
    def __init__(self, collection: PyMongoCollection):
        if not isinstance(collection, PyMongoCollection):
            raise ValueError("PyMongoCollection is required")
        self.collection = collection

    def get_concept(self, concept_id: str) -> AnatomicLocation:
        raw_result = self.collection.find_one({"_id": concept_id})
        return AnatomicLocation.model_validate(raw_result)

    def get_concepts(self, concept_ids: list[str]) -> list[AnatomicLocation]:
        raw_results = self.collection.find(self._args_for_find_multiple_ids(concept_ids))
        return self._process_find_results(raw_results)

    def text_search(self, search_term: str, count: int) -> list[SearchResult]:
        raw_results = self.collection.aggregate(self._text_search_pipeline(search_term, count))
        return self._process_text_search_results(raw_results)

    def get_random_concepts(self, count: int) -> list[AnatomicLocation]:
        raw_results = self.collection.aggregate(self._args_for_get_sample(count))
        return self._process_find_results(raw_results)

    def update_embedding_vector(self, concept: AnatomicLocation, vector: list[float]) -> bool:
        result = self.collection.update_one(*self._embedding_vector_update_args(concept, vector))
        return self._manage_vector_write_update_result(result, concept, vector)

    def get_count(self):
        return self.collection.count_documents({})

    def get_search_results(self, search_term: str, count: int = 50) -> list[SearchResult]:
        pipeline = self._text_search_pipeline(search_term, count)
        raw_results = self.collection.aggregate(pipeline)
        return self._process_text_search_results(raw_results)

    def write_embedding_vector(self, concept: AnatomicLocation, vector: list[float]) -> bool:
        filter_args, update_args = self._embedding_vector_update_args(concept, vector)
        result = self.collection.update_one(filter_args, update_args)
        return self._manage_vector_write_update_result(result, concept, vector)

    def bulk_write_embedding_vectors(self, concepts: list[AnatomicLocation], vectors: list[list[float]]) -> bool:
        update_commands = self._update_commands_to_write_embedding_vectors(concepts, vectors)
        result = self.collection.bulk_write(update_commands)
        return self._manage_bulk_write_result(result, concepts, vectors)
