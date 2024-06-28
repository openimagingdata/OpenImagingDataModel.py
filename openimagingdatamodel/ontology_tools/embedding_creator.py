import tiktoken
from openai import AsyncOpenAI, OpenAI
from openai.types import CreateEmbeddingResponse

from .concept import Concept

DEFAULT_DIMENSIONS = 1536
DEFAULT_MODEL = "text-embedding-3-large"
TOKEN_LIMIT = 8191

TOKENIZER = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(TOKENIZER.encode(text))


class AbstractEmbeddingCreator:
    def get_text_for_embedding(self, concept: Concept) -> str:
        return concept.text_for_embedding().replace("\n", " ")

    def get_token_count_for_texts(self, texts: list[str]) -> int:
        return sum(count_tokens(text) for text in texts)

    def get_multiple_texts_for_embedding(self, concepts: list[Concept]) -> list[str]:
        texts = [self.get_text_for_embedding(concept) for concept in concepts]

        if token_count := self.get_token_count_for_texts(texts) > TOKEN_LIMIT:
            raise ValueError(f"Token count {token_count} exceeds limit of {TOKEN_LIMIT}")
        return texts

    def get_embedding_vector_from_response(self, response: CreateEmbeddingResponse) -> list[float]:
        return response.data[0].embedding

    def get_multiple_embedding_vectors_from_response(self, response: CreateEmbeddingResponse) -> list[list[float]]:
        return [item.embedding for item in response.data]


class EmbeddingCreator(AbstractEmbeddingCreator):
    def __init__(self, client: OpenAI):
        self.client = client

    def create_embedding_for_concept(
        self, concept: Concept, /, model: str = DEFAULT_MODEL, dimensions: int = DEFAULT_DIMENSIONS
    ) -> list[float]:
        text = concept.text_for_embedding()
        response = self.client.embeddings.create(input=[text], model=model, dimensions=dimensions)
        return self.get_embedding_vector_from_response(response)

    def create_embeddings_for_concepts(
        self, concepts: list[Concept], /, model: str = DEFAULT_MODEL, dimensions: int = DEFAULT_DIMENSIONS
    ) -> list[list[float]]:
        texts = self.get_multiple_texts_for_embedding(concepts)
        response = self.client.embeddings.create(input=texts, model=model, dimensions=dimensions)
        return self.get_multiple_embedding_vectors_from_response(response)

    def create_embedding_for_text(
        self, text: str, /, model: str = DEFAULT_MODEL, dimensions: int = DEFAULT_DIMENSIONS
    ) -> list[float]:
        response = self.client.embeddings.create(input=[text], model=model, dimensions=dimensions)
        return self.get_embedding_vector_from_response(response)


class AsyncEmbeddingCreator(AbstractEmbeddingCreator):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def create_embedding_for_concept(
        self, concept: Concept, /, model=DEFAULT_MODEL, dimensions: int = DEFAULT_DIMENSIONS
    ) -> list[float]:
        text = self.get_text_for_embedding(concept)
        response = await self.client.embeddings.create(input=[text], model=model, dimensions=dimensions)
        return self.get_embedding_vector_from_response(response)

    async def create_embeddings_for_concepts(
        self, concepts: list[Concept], /, model=DEFAULT_MODEL, dimensions: int = DEFAULT_DIMENSIONS
    ) -> list[list[float]]:
        texts = self.get_multiple_texts_for_embedding(concepts)
        response = await self.client.embeddings.create(input=texts, model=model, dimensions=dimensions)
        return self.get_multiple_embedding_vectors_from_response(response)

    async def create_embedding_for_text(
        self, text: str, /, model=DEFAULT_MODEL, dimensions: int = DEFAULT_DIMENSIONS
    ) -> list[float]:
        response = await self.client.embeddings.create(input=text, model=model, dimensions=dimensions)
        return self.get_embedding_vector_from_response(response)