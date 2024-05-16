from motor.motor_asyncio import AsyncIOMotorCollection

from .snomedct_concept import SnomedCTConcept


class SnomedCTConceptRepo:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def get_concept(self, concept_id: str) -> SnomedCTConcept:
        concept = await self.collection.find_one({"conceptId": concept_id})
        return SnomedCTConcept.model_validate(concept)
