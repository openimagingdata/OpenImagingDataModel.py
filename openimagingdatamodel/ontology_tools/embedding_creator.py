from openai import AsyncOpenAI, CreateEmbeddingResponse, OpenAI

from .snomedct_concept import SnomedCTConcept

DEFAULT_DIMENSIONS = 1536
DEFAULT_MODEL = "text-embedding-3-large"


class AbstractEmbeddingCreator:
    def get_text_for_embedding(self, concept: SnomedCTConcept) -> str:
        return concept.text_for_embedding().replace("\n", " ")

    def get_embedding_vector_from_response(self, response: CreateEmbeddingResponse) -> list[float]:
        return response.data[0].embedding


class EmbeddingCreator(AbstractEmbeddingCreator):
    def __init__(self, client: OpenAI):
        self.client = client

    def create_embedding_for_snomedctconcept(
        self, concept: SnomedCTConcept, /, model=DEFAULT_MODEL, dimensions: int = DEFAULT_DIMENSIONS
    ):
        text = self.get_text_for_embedding(concept)
        response = self.client.embeddings.create(input=[text], model=model, dimensions=dimensions)
        return self.get_embedding_vector_from_response(response)


class AsyncEmbeddingCreator(AbstractEmbeddingCreator):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def create_embedding_for_snomedctconcept(
        self, concept: SnomedCTConcept, /, model=DEFAULT_MODEL, dimensions: int = DEFAULT_DIMENSIONS
    ):
        text = self.get_text_for_embedding(concept)
        response = await self.client.embeddings.create(input=[text], model=model, dimensions=dimensions)
        return self.get_embedding_vector_from_response(response)
