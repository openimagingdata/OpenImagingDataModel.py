from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from .snomedct_concept import SnomedCTConcept


class SnomedCTSearchResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel, validate_assignment=True)

    concept_id: str
    preferred_term: str
    semantic_tags: list[str]
    score: float


class SnomedCTConceptRepo:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def get_concept(self, concept_id: str) -> SnomedCTConcept:
        concept = await self.collection.find_one({"conceptId": concept_id})
        return SnomedCTConcept.model_validate(concept)

    # TODO: Implement the following methods
    # - Get count of all concepts
    # - Do a basic text search (need index on preferredTerm field)
    # - Use Atlas full-text search to do a text search

    async def get_search_results(self, search_term: str, count: int = 50) -> list[SnomedCTConcept]:
        pipeline = [
            {"$search": {"index": "defaultText", "text": {"query": search_term, "path": {"wildcard": "*"}}}},
            {"$limit": count},
            {
                "$project": {
                    "_id": 0,
                    "conceptId": 1,
                    "preferredTerm": 1,
                    "semanticTags": 1,
                    "score": {"$meta": "searchScore"},
                }
            },
        ]
        raw_results = await self.collection.aggregate(pipeline).to_list(count)
        return [SnomedCTSearchResult.model_validate(result) for result in raw_results]

    # - Write vectors back to the database for a batch of concepts
    # - Define a vector index
    # - Do a vector search