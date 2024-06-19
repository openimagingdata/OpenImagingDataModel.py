from pprint import pprint as pp  # noqa: F401
from typing import Any, ClassVar, Generic, Mapping, TypeVar

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection as PyMongoCollection
from pymongo.collection import UpdateOne
from pymongo.results import BulkWriteResult

from .anatomic_location import AnatomicLocation
from .concept import Concept
from .radlex_concept import RadLexConcept
from .search_result import SearchResult
from .snomedct_concept import SnomedCTConcept

TConcept = TypeVar("TConcept", bound=type[Concept])


def args_for_find_one(code_field: str, search_code: str) -> Mapping[str, Any]:
    return {code_field: search_code}


def args_for_multiple_ids(code_field: str, concept_ids: list[str]) -> Mapping[str, Any]:
    return {code_field: {"$in": concept_ids}}


def args_for_unembedded(embedding_vector_field: str) -> Mapping[str, Any]:
    return {embedding_vector_field: {"$exists": False}}


def args_for_sample(count: int) -> Mapping[str, Any]:
    return [{"$sample": {"size": count}}]


def text_search_pipeline(
    index_name: str, code_field: str, system_name: str, display_field: str, search_term: str, count: int
) -> list[Mapping[str, Any]]:
    return [
        {"$search": {"index": index_name, "text": {"query": search_term, "path": {"wildcard": "*"}}}},
        {"$limit": count},
        {
            "$project": {
                "_id": 0,
                "system": system_name,
                "code": f"${code_field}",
                "display": f"${display_field}",
                "score": {"$meta": "searchScore"},
            }
        },
    ]


DEFAULT_COUNT_TO_CANDIDATES_RATIO = 15


def vector_search_pipeline(
    index_name: str,
    embedding_field_name: str,
    code_field: str,
    system_name: str,
    display_field: str,
    query_embedding: list[float],
    count: int,
) -> list[Mapping[str, Any]]:
    return [
        {
            "$vectorSearch": {
                "index": index_name,
                "path": embedding_field_name,
                "queryVector": query_embedding,
                "numCandidates": count * DEFAULT_COUNT_TO_CANDIDATES_RATIO,
                "limit": count,
            }
        },
        {
            "$project": {
                "_id": 0,
                "system": system_name,
                "code": f"${code_field}",
                "display": f"${display_field}",
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]


def concepts_from_raw_results(concept_class: TConcept, raw_results: Any) -> list[TConcept]:
    return [concept_class.model_validate(raw_result) for raw_result in raw_results]


def search_results_from_raw_results(raw_results: Any) -> list[SearchResult]:
    return [SearchResult.model_validate(raw_result) for raw_result in raw_results]


def update_commands_to_write_embedding_vectors(
    embedding_vector_field: str, concepts: list[Concept], vectors: list[list[float]]
) -> list[dict]:
    return [
        UpdateOne({"_id": concept.id}, {"$set": {embedding_vector_field: vector}})
        for concept, vector in zip(concepts, vectors)
    ]


def manage_bulk_write_result(result: BulkWriteResult, concepts: list[Concept], vectors: list[list[float]]) -> bool:
    if result.modified_count == len(concepts):
        for concept, vector in zip(concepts, vectors):
            concept.embedding_vector = vector
        return True
    return False


class Repository(Generic[TConcept]):
    CODE_FIELD: ClassVar[str] = "_id"
    DISPLAY_FIELD: ClassVar[str] = "description"
    EMBEDDING_VECTOR_FIELD: ClassVar[str] = "embedding_vector"
    TEXT_SEARCH_INDEX_NAME: ClassVar[str] = "defaultText"
    VECTOR_SEARCH_INDEX_NAME: ClassVar[str] = "defaultVector"

    def __init__(self, concept_class: TConcept, collection: PyMongoCollection):
        self.concept_class: TConcept = concept_class
        assert issubclass(concept_class, Concept)
        self.collection: PyMongoCollection = collection

    def get_count(self) -> int:
        return self.collection.count_documents({})

    def get_concept(self, concept_id: str) -> TConcept:
        args = args_for_find_one(self.CODE_FIELD, concept_id)
        raw_return = self.collection.find_one(args)
        return self.concept_class.model_validate(raw_return)

    def get_concepts(self, concept_ids: list[str]) -> list[TConcept]:
        args = args_for_multiple_ids(self.CODE_FIELD, concept_ids)
        raw_results = self.collection.find(args)
        return concepts_from_raw_results(self.concept_class, raw_results)

    def get_random_concepts(self, count: int) -> TConcept | list[TConcept]:
        raw_results = self.collection.aggregate(args_for_sample(count))
        concepts = concepts_from_raw_results(self.concept_class, raw_results)
        return concepts[0] if count == 1 and len(concepts) == 1 else concepts

    def get_unembedded_concepts(self, count) -> list[TConcept]:
        raw_results = self.collection.find(args_for_unembedded(self.EMBEDDING_VECTOR_FIELD)).limit(count)
        return concepts_from_raw_results(self.concept_class, raw_results)

    def text_search(self, search_term: str, count: int) -> list[SearchResult]:
        pipeline = text_search_pipeline(
            self.TEXT_SEARCH_INDEX_NAME,
            self.CODE_FIELD,
            self.concept_class.SYSTEM_NAME,
            self.DISPLAY_FIELD,
            search_term,
            count,
        )
        pp(pipeline)
        raw_results = self.collection.aggregate(pipeline)
        return search_results_from_raw_results(raw_results)

    def vector_search(self, query_embedding: list[float], count: int) -> list[SearchResult]:
        pipeline = vector_search_pipeline(
            self.VECTOR_SEARCH_INDEX_NAME,
            self.EMBEDDING_VECTOR_FIELD,
            self.CODE_FIELD,
            self.concept_class.SYSTEM_NAME,
            self.DISPLAY_FIELD,
            query_embedding,
            count,
        )
        raw_results = self.collection.aggregate(pipeline)
        return search_results_from_raw_results(raw_results)

    def write_embedding_vectors(self, concepts: list[Concept], vectors: list[list[float]]) -> bool:
        commands = update_commands_to_write_embedding_vectors(self.EMBEDDING_VECTOR_FIELD, concepts, vectors)
        result = self.collection.bulk_write(commands)
        return manage_bulk_write_result(result, concepts, vectors)


class AsyncRepository(Generic[TConcept]):
    CODE_FIELD: ClassVar[str] = "_id"
    DISPLAY_FIELD: ClassVar[str] = "description"
    EMBEDDING_VECTOR_FIELD: ClassVar[str] = "embedding_vector"
    TEXT_SEARCH_INDEX_NAME: ClassVar[str] = "defaultText"
    VECTOR_SEARCH_INDEX_NAME: ClassVar[str] = "defaultVector"

    def __init__(self, concept_class: TConcept, collection: AsyncIOMotorCollection):
        self.concept_class: TConcept = concept_class
        assert issubclass(concept_class, Concept)
        self.collection: AsyncIOMotorCollection = collection

    async def get_count(self) -> int:
        return await self.collection.count_documents({})

    async def get_concept(self, concept_id: str) -> TConcept:
        args = args_for_find_one(self.CODE_FIELD, concept_id)
        raw_return = await self.collection.find_one(args)
        return self.concept_class.model_validate(raw_return)

    async def get_concepts(self, concept_ids: list[str]) -> list[TConcept]:
        args = args_for_multiple_ids(self.CODE_FIELD, concept_ids)
        raw_results = await self.collection.find(args).to_list(len(concept_ids))
        return concepts_from_raw_results(self.concept_class, raw_results)

    async def get_random_concepts(self, count: int) -> TConcept | list[TConcept]:
        raw_results = await self.collection.aggregate(args_for_sample(count)).to_list(count)
        concepts = concepts_from_raw_results(self.concept_class, raw_results)
        return concepts[0] if count == 1 and len(concepts) == 1 else concepts

    async def get_unembedded_concepts(self, count) -> list[TConcept]:
        cursor = self.collection.find(args_for_unembedded(self.EMBEDDING_VECTOR_FIELD)).limit(count)
        raw_results = await cursor.to_list(count)
        return concepts_from_raw_results(self.concept_class, raw_results)

    async def text_search(self, search_term: str, count: int) -> list[SearchResult]:
        pipeline = text_search_pipeline(
            self.TEXT_SEARCH_INDEX_NAME,
            self.CODE_FIELD,
            self.concept_class.SYSTEM_NAME,
            self.DISPLAY_FIELD,
            search_term,
            count,
        )
        raw_results = await self.collection.aggregate(pipeline).to_list(count)
        return search_results_from_raw_results(raw_results)

    async def vector_search(self, query_embedding: list[float], count: int) -> list[SearchResult]:
        pipeline = vector_search_pipeline(
            self.VECTOR_SEARCH_INDEX_NAME,
            self.EMBEDDING_VECTOR_FIELD,
            self.CODE_FIELD,
            self.concept_class.SYSTEM_NAME,
            self.DISPLAY_FIELD,
            query_embedding,
            count,
        )
        raw_results = await self.collection.aggregate(pipeline).to_list(count)
        return search_results_from_raw_results(raw_results)

    async def write_embedding_vectors(self, concepts: list[Concept], vectors: list[list[float]]) -> bool:
        commands = update_commands_to_write_embedding_vectors(self.EMBEDDING_VECTOR_FIELD, concepts, vectors)
        result = await self.collection.bulk_write(commands)
        return manage_bulk_write_result(result, concepts, vectors)


class AnatomicLocationRepository(Repository[AnatomicLocation]):
    CODE_FIELD: ClassVar[str] = "_id"
    DISPLAY_FIELD: ClassVar[str] = "description"
    EMBEDDING_VECTOR_FIELD: ClassVar[str] = "embedding_vector"
    TEXT_SEARCH_INDEX_NAME: ClassVar[str] = "defaultText"
    VECTOR_SEARCH_INDEX_NAME: ClassVar[str] = "defaultVector"

    def __init__(self, collection: PyMongoCollection):
        super().__init__(AnatomicLocation, collection)


class AsyncAnatomicLocationRepository(AsyncRepository[AnatomicLocation]):
    CODE_FIELD: ClassVar[str] = "_id"
    DISPLAY_FIELD: ClassVar[str] = "description"
    EMBEDDING_VECTOR_FIELD: ClassVar[str] = "embedding_vector"
    TEXT_SEARCH_INDEX_NAME: ClassVar[str] = "defaultText"
    VECTOR_SEARCH_INDEX_NAME: ClassVar[str] = "defaultVector"

    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(AnatomicLocation, collection)


class RadlexConceptRepository(Repository[RadLexConcept]):
    CODE_FIELD: ClassVar[str] = "_id"
    DISPLAY_FIELD: ClassVar[str] = "preferredLabel"
    EMBEDDING_VECTOR_FIELD: ClassVar[str] = "embedding_vector"
    TEXT_SEARCH_INDEX_NAME: ClassVar[str] = "defaultText"
    VECTOR_SEARCH_INDEX_NAME: ClassVar[str] = "defaultVector"

    def __init__(self, collection: PyMongoCollection):
        super().__init__(RadLexConcept, collection)


class AsyncRadlexConceptRepository(AsyncRepository[RadLexConcept]):
    CODE_FIELD: ClassVar[str] = "_id"
    DISPLAY_FIELD: ClassVar[str] = "preferredLabel"
    EMBEDDING_VECTOR_FIELD: ClassVar[str] = "embedding_vector"
    TEXT_SEARCH_INDEX_NAME: ClassVar[str] = "defaultText"
    VECTOR_SEARCH_INDEX_NAME: ClassVar[str] = "defaultVector"

    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(RadLexConcept, collection)


class SnomedCTConceptRepository(Repository[SnomedCTConcept]):
    CODE_FIELD: ClassVar[str] = "concept_id"
    DISPLAY_FIELD: ClassVar[str] = "preferredTerm"
    EMBEDDING_VECTOR_FIELD: ClassVar[str] = "embedding_vector"
    TEXT_SEARCH_INDEX_NAME: ClassVar[str] = "defaultText"
    VECTOR_SEARCH_INDEX_NAME: ClassVar[str] = "defaultVector"

    def __init__(self, collection: PyMongoCollection):
        super().__init__(SnomedCTConcept, collection)


class AsyncSnomedCTConceptRepository(AsyncRepository[SnomedCTConcept]):
    CODE_FIELD: ClassVar[str] = "concept_id"
    DISPLAY_FIELD: ClassVar[str] = "preferredTerm"
    EMBEDDING_VECTOR_FIELD: ClassVar[str] = "embedding_vector"
    TEXT_SEARCH_INDEX_NAME: ClassVar[str] = "defaultText"
    VECTOR_SEARCH_INDEX_NAME: ClassVar[str] = "defaultVector"

    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(SnomedCTConcept, collection)


if __name__ == "__main__":
    import asyncio  # noqa: F401

    from dotenv import dotenv_values
    from motor.motor_asyncio import AsyncIOMotorClient
    from pymongo import MongoClient

    from .embedding_creator import AsyncEmbeddingCreator, EmbeddingCreator

    config = dotenv_values(".env")
    db_name = "ontologies"

    def get_sync_collection(collection_name: str) -> PyMongoCollection:
        client: MongoClient = MongoClient(config["ATLAS_DSN"])
        return client[db_name][collection_name]

    def get_async_collection(collection_name: str) -> AsyncIOMotorCollection:
        client = AsyncIOMotorClient(config["ATLAS_DSN"])
        return client[db_name][collection_name]

    def get_embedding_creator() -> EmbeddingCreator:
        from openai import OpenAI

        llm = OpenAI(api_key=config["OPENAI_API_KEY"])
        return EmbeddingCreator(llm)

    def get_async_embedding_creator() -> AsyncEmbeddingCreator:
        from openai import AsyncOpenAI

        llm = AsyncOpenAI(api_key=config["OPENAI_API_KEY"])
        return AsyncEmbeddingCreator(llm)

    def sync_anatomic_location_check():
        repo = AnatomicLocationRepository(get_sync_collection("anatomic_locations"))
        print(repo.get_count())
        concept = repo.get_concept("RID56")
        concept.print()

    def sync_radlex_concept_check():
        repo = RadlexConceptRepository(get_sync_collection("radlex"))
        print(repo.get_count())
        concept = repo.get_concept("RID56")
        concept.print()

    def sync_snomedct_concept_check():
        repo = SnomedCTConceptRepository(get_sync_collection("snomedct"))
        print(repo.get_count())
        concept = repo.get_concept("9775002")
        concept.print()

    async def async_anatomic_location_check():
        async_repo = AsyncAnatomicLocationRepository(get_async_collection("anatomic_locations"))
        concept = await async_repo.get_concept("RID56")
        concept.print()

    async def async_radlex_concept_check():
        async_repo = AsyncAnatomicLocationRepository(get_async_collection("anatomic_locations"))
        concept = await async_repo.get_concept("RID56")
        concept.print()

    async def async_snomedct_concept_check():
        async_repo = AsyncSnomedCTConceptRepository(get_async_collection("snomedct"))
        concept = await async_repo.get_concept("9775002")
        concept.print()

    def anatomic_location_searches():
        repo = AnatomicLocationRepository(get_sync_collection("anatomic_locations"))
        embedding_creator = get_embedding_creator()
        print(repo.get_count())

        concept = repo.get_concept("RID56")
        concept.print()

        concepts = repo.get_concepts(["RID56", "RID1302"])
        for concept in concepts:
            concept.print()

        random_concept = repo.get_random_concepts(1)
        random_concept.print()

        search_results = repo.text_search("brain", 5)
        for search_result in search_results:
            search_result.print()

        query_vector = embedding_creator.create_embedding_for_text("brain")
        search_results = repo.vector_search(query_vector, 5)
        for search_result in search_results:
            search_result.print()

    async def async_anatomic_location_searches():
        async_repo = AsyncAnatomicLocationRepository(get_async_collection("anatomic_locations"))
        async_embedding_creator = get_async_embedding_creator()

        print(await async_repo.get_count())

        concept = await async_repo.get_concept("RID56")
        concept.print()

        concepts = await async_repo.get_concepts(["RID56", "RID1302"])
        for concept in concepts:
            concept.print()

        random_concept = await async_repo.get_random_concepts(1)
        random_concept.print()

        search_results = await async_repo.text_search("brain", 5)
        for search_result in search_results:
            search_result.print()

        query_vector = await async_embedding_creator.create_embedding_for_text("brain")
        search_results = await async_repo.vector_search(query_vector, 5)
        for search_result in search_results:
            search_result.print()

    def radlex_concept_searches():
        repo = RadlexConceptRepository(get_sync_collection("radlex"))
        # embedding_creator = get_embedding_creator()
        print(repo.get_count())

        concept = repo.get_concept("RID56")
        concept.print()

        concepts = repo.get_concepts(["RID56", "RID1302"])
        for concept in concepts:
            concept.print()

        random_concept = repo.get_random_concepts(1)
        random_concept.print()

        search_results = repo.text_search("brain", 5)
        for search_result in search_results:
            search_result.print()

        # query_vector = embedding_creator.create_embedding_for_text("brain")
        # search_results = repo.vector_search(query_vector, 5)
        # for search_result in search_results:
        #     search_result.print()

    async def async_radlex_concept_searches():
        async_repo = AsyncRadlexConceptRepository(get_async_collection("radlex"))
        # async_embedding_creator = get_async_embedding_creator()
        print(await async_repo.get_count())

        concept = await async_repo.get_concept("RID56")
        concept.print()

        concepts = await async_repo.get_concepts(["RID56", "RID1302"])
        for concept in concepts:
            concept.print()

        random_concept = await async_repo.get_random_concepts(1)
        random_concept.print()

        search_results = await async_repo.text_search("brain", 5)
        for search_result in search_results:
            search_result.print()

        # query_vector = await async_embedding_creator.create_embedding_for_text("brain")
        # search_results = await async_repo.vector_search(query_vector, 5)
        # for search_result in search_results:
        #     search_result.print()

    def radlex_generate_embeddings():
        collection = get_sync_collection("radlex")
        repo = RadlexConceptRepository(collection)
        embedding_creator = get_embedding_creator()
        concepts = repo.get_unembedded_concepts(400)
        texts = [concept.text_for_embedding() for concept in concepts]
        token_count = embedding_creator.get_token_count_for_texts(texts)
        print(f"{token_count=}")
        vectors = embedding_creator.create_embeddings_for_concepts(concepts)
        print(f"{len(vectors)=}")
        if all(len(v) == 1536 for v in vectors):
            print("All vectors have correct length")
        else:
            raise ValueError("Not all vectors have correct length")

        if repo.write_embedding_vectors(concepts, vectors):
            print("Successfully wrote vectors")

    async def async_radlex_generate_embeddings():
        collection = get_async_collection("radlex")
        repo = AsyncRadlexConceptRepository(collection)
        embedding_creator = get_async_embedding_creator()

        concepts = await repo.get_unembedded_concepts(4000)
        batch_size = 400

        async def do_embedding(batch_number: int, concepts: list[RadLexConcept]):
            texts = [concept.text_for_embedding() for concept in concepts]
            token_count = embedding_creator.get_token_count_for_texts(texts)
            print(f"Task {batch_number=}: {token_count=}")
            vectors = await embedding_creator.create_embeddings_for_concepts(concepts)
            print(f"Task {batch_number=}: {len(vectors)=}")
            if all(len(v) == 1536 for v in vectors):
                print(f"Task {batch_number=}: All vectors have correct length")
            else:
                raise ValueError(f"Task {batch_number=}: Not all vectors have correct length")

            if await repo.write_embedding_vectors(concepts, vectors):
                print(f"Task {batch_number=}: Successfully wrote vectors")

        tasks = [
            do_embedding(i // batch_size, concepts[i : i + batch_size]) for i in range(0, len(concepts), batch_size)
        ]
        await asyncio.gather(*tasks)

    # radlex_generate_embeddings()
    asyncio.run(async_radlex_generate_embeddings())

    # sync_anatomic_location_check()
    # asyncio.run(async_anatomic_location_check())
    # sync_radlex_concept_check()
    # asyncio.run(async_radlex_concept_check())
    # asyncio.run(async_anatomic_location_searches())
    # anatomic_location_searches()
    # sync_snomedct_concept_check()
    # asyncio.run(async_snomedct_concept_check())
    # radlex_concept_searches()
    # asyncio.run(async_radlex_concept_searches())
