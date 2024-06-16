from typing import Any, Mapping

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection as PyMongoCollection
from pymongo.results import UpdateResult

from .radlex_concept import RadLexConcept
from .search_result import SearchResult


class AbstractRadLexConceptRepo:
    def __init__(self) -> None:
        raise NotImplementedError

    def _text_search_pipeline(self, search_term: str, count: int) -> list[Mapping[str, Any]]:
        return [
            {"$search": {"index": "defaultText", "text": {"query": search_term, "path": {"wildcard": "*"}}}},
            {"$limit": count},
            {
                "$project": {
                    "_id": 0,
                    "system": "RadLex",
                    "code": "$_id",
                    "display": "$preferredLabel",
                    "score": {"$meta": "searchScore"},
                }
            },
        ]

    def _args_for_find_multiple_ids(self, concept_ids: list[str]) -> Mapping[str, Any]:
        return {"_id": {"$in": concept_ids}}

    def _args_for_get_sample(self, count: int) -> list[Mapping[str, Any]]:
        return [{"$sample": {"size": count}}]

    def _process_find_results(self, raw_results) -> list[RadLexConcept]:
        return [RadLexConcept.model_validate(result) for result in raw_results]

    def _process_text_search_results(self, raw_results) -> list[SearchResult]:
        return [SearchResult.model_validate(result) for result in raw_results]

    def _embedding_vector_update_args(self, concept: RadLexConcept, vector: list[float]) -> tuple[dict, dict]:
        return ({"_id": concept.id}, {"$set": {"embedding_vector": vector}})

    def _manage_vector_write_update_result(
        self, result: UpdateResult, concept: RadLexConcept, vector: list[float]
    ) -> bool:
        if result.modified_count == 1:
            concept.embedding_vector = vector
            return True
        return False


class AsyncRadLexConceptRepo(AbstractRadLexConceptRepo):
    def __init__(self, collection: AsyncIOMotorCollection):
        if not isinstance(collection, AsyncIOMotorCollection):
            raise ValueError("AsyncIOMotorCollection is required")
        self.collection = collection

    async def get_concept(self, concept_id: str) -> RadLexConcept:
        raw_concept = await self.collection.find_one({"_id": concept_id})
        return RadLexConcept.model_validate(raw_concept)

    async def get_concepts(self, concept_ids: list[str]) -> list[RadLexConcept]:
        args = self._args_for_find_multiple_ids(concept_ids)
        raw_results = await self.collection.find(args).to_list(len(concept_ids))
        return self._process_find_results(raw_results)

    async def get_random_concepts(self, count: int) -> list[RadLexConcept]:
        args = self._args_for_get_sample(count)
        raw_results = await self.collection.aggregate(args).to_list(count)
        return self._process_find_results(raw_results)

    async def get_count(self):
        return await self.collection.count_documents({})

    async def get_search_results(self, search_term: str, count: int = 50) -> list[SearchResult]:
        pipeline = self._text_search_pipeline(search_term, count)
        raw_results = await self.collection.aggregate(pipeline).to_list(count)
        return self._process_text_search_results(raw_results)

    async def write_embedding_vector(self, concept: RadLexConcept, vector: list[float]) -> bool:
        filter_args, update_args = self._embedding_vector_update_args(concept, vector)
        result = await self.collection.update_one(filter_args, update_args)
        return self._manage_vector_write_update_result(result, concept, vector)


class RadLexConceptRepo(AbstractRadLexConceptRepo):
    def __init__(self, collection: PyMongoCollection):
        if not isinstance(collection, PyMongoCollection):
            raise ValueError("pymongo.collection.Collection is required")
        self.collection = collection

    def get_concept(self, concept_id: str) -> RadLexConcept:
        raw_concept = self.collection.find_one({"_id": concept_id})
        return RadLexConcept.model_validate(raw_concept)

    def get_concepts(self, concept_ids: list[str]) -> list[RadLexConcept]:
        args = self._args_for_find_multiple_ids(concept_ids)
        raw_results = self.collection.find(args)
        return self._process_find_results(raw_results)

    def get_random_concepts(self, count: int) -> list[RadLexConcept]:
        args = self._args_for_get_sample(count)
        raw_results = self.collection.aggregate(args)
        return self._process_find_results(raw_results)

    def get_count(self):
        return self.collection.count_documents({})

    def get_search_results(self, search_term: str, count: int = 50) -> list[SearchResult]:
        pipeline = self._text_search_pipeline(search_term, count)
        raw_results = self.collection.aggregate(pipeline)
        return self._process_text_search_results(raw_results)

    def write_embedding_vector(self, concept: RadLexConcept, vector: list[float]) -> bool:
        filter_args, update_args = self._embedding_vector_update_args(concept, vector)
        result = self.collection.update_one(filter_args, update_args)
        return self._manage_vector_write_update_result(result, concept, vector)
