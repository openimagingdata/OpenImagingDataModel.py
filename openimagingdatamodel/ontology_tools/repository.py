from typing import Any, ClassVar, Generic, TypeVar

from motor.motor_asyncio import AsyncIOMotorCollection

from .anatomic_location import AnatomicLocation
from .concept import Concept
from .radlex_concept import RadLexConcept
from .search_result import SearchResult
from .snomedct_concept import SnomedCTConcept

TConcept = TypeVar("TConcept", bound=type[Concept])


SEMANTIC_TAGS = [
    "disorder",
    "procedure",
    "finding",
    "body structure",
    "qualifier value",
    "observable entity",
    "context-dependent category",
    "morphologic abnormality",
    "regime/therapy",
    "assessment scale",
    "function",
    "attribute",
    "tumor staging",
    "biological function",
    "contextual qualifier",
]


def concepts_from_raw_results(concept_class: TConcept, raw_results: Any) -> list[TConcept]:
    return [concept_class.model_validate(raw_result) for raw_result in raw_results]  # type: ignore


def search_results_from_raw_results(raw_results: Any) -> list[SearchResult]:
    return [SearchResult.model_validate(raw_result) for raw_result in raw_results]


class Repository(Generic[TConcept]):
    CODE_FIELD: ClassVar[str] = "_id"
    DISPLAY_FIELD: ClassVar[str] = "description"

    def __init__(self, concept_class: TConcept, collection: AsyncIOMotorCollection):
        self.concept_class: TConcept = concept_class
        assert issubclass(concept_class, Concept)
        self.collection: AsyncIOMotorCollection = collection

    async def get_count(self) -> int:
        return await self.collection.estimated_document_count()

    async def get_concept(self, concept_id: str) -> TConcept:
        search_args = {self.CODE_FIELD: concept_id}
        raw_return = await self.collection.find_one(search_args)
        return self.concept_class.model_validate(raw_return) if raw_return else None  # type: ignore

    async def get_concepts(self, concept_ids: list[str]) -> list[TConcept]:
        search_args = {self.CODE_FIELD: {"$in": concept_ids}}
        raw_results = await self.collection.find(search_args).to_list(len(concept_ids))
        return concepts_from_raw_results(self.concept_class, raw_results)

    async def get_random_concepts(self, count: int = 1) -> TConcept | list[TConcept]:
        raw_results = await self.collection.aggregate([{"$sample": {"size": count}}]).to_list(count)
        concepts = concepts_from_raw_results(self.concept_class, raw_results)
        return concepts[0] if count == 1 and len(concepts) == 1 else concepts


class AnatomicLocationRepository(Repository[AnatomicLocation]):  # type: ignore
    CODE_FIELD: ClassVar[str] = "_id"
    DISPLAY_FIELD: ClassVar[str] = "description"

    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(AnatomicLocation, collection)  # type: ignore


class RadlexConceptRepository(Repository[RadLexConcept]):  # type: ignore
    CODE_FIELD: ClassVar[str] = "_id"
    DISPLAY_FIELD: ClassVar[str] = "preferredLabel"

    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(RadLexConcept, collection)  # type: ignore


class SnomedCTConceptRepository(Repository[SnomedCTConcept]):  # type: ignore
    CODE_FIELD: ClassVar[str] = "_id"
    DISPLAY_FIELD: ClassVar[str] = "preferredTerm"

    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(SnomedCTConcept, collection)  # type: ignore


if __name__ == "__main__":
    import asyncio  # noqa: F401

    from dotenv import dotenv_values
    from motor.motor_asyncio import AsyncIOMotorClient

    config = dotenv_values(".env")
    db_name = "ontologies"

    def get_collection(collection_name: str) -> AsyncIOMotorCollection:
        client: AsyncIOMotorClient = AsyncIOMotorClient(config["ATLAS_DSN"])
        return client[db_name][collection_name]

    async def get_counts(repo: Repository):
        print("Getting counts from repository...")
        count = await repo.get_count()
        print(f"Estimated document count from repository: {count}")

    async def get_random_concepts(repo: Repository, count: int = 1):
        print("Getting random concepts from repository...")
        concepts = await repo.get_random_concepts(count)
        concept_json_string = "\n===\n".join([
            concept.model_dump_json(exclude_none=True, indent=2) for concept in concepts
        ])
        print(f"Random concepts from repository\n================\n{concept_json_string}")

    async def main():
        repo = RadlexConceptRepository(get_collection("radlex"))
        await get_counts(repo)
        await get_random_concepts(repo, 5)

    asyncio.run(main())
