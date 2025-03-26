from os import getenv

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from openai import AsyncOpenAI

from . import repository


class Config:
    def __init__(
        self,
        dotenv_path: str = ".env",
        openai_api_key: str | None = None,
        atlas_dsn: str | None = None,
        database_name: str | None = None,
    ):
        if dotenv_path:
            load_dotenv(dotenv_path)

        self.OPENAI_API_KEY = openai_api_key or getenv("OPENAI_API_KEY")
        if not self.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found in environment or .env file (OPENAI_API_KEY).")
        self.ATLAS_DSN = atlas_dsn or getenv("ATLAS_DSN")
        if not self.ATLAS_DSN:
            raise ValueError("MongoDB Atlas DSN not found in environment or .env file (ATLAS_DSN).")
        self.DATABASE_NAME = database_name or getenv("DATABASE_NAME") or "ontologies"

        self._KNOWN_ONTOLOGIES = ("snomedct", "radlex", "anatomic_locations")

        self._async_llm: AsyncOpenAI | None = None
        self._async_db_client: AsyncIOMotorClient | None = None

    @property
    def llm(self) -> AsyncOpenAI:
        if self._async_llm is None:
            self._async_llm = AsyncOpenAI(api_key=self.OPENAI_API_KEY)
        return self._async_llm

    @property
    def db_client(self) -> AsyncIOMotorClient:
        if self._async_db_client is None:
            self._async_db_client = AsyncIOMotorClient(self.ATLAS_DSN)
        return self._async_db_client

    @property
    def known_ontologies(self) -> tuple[str, ...]:
        return self._KNOWN_ONTOLOGIES

    def get_repository(self, ontology: str) -> repository.Repository:
        db = self.db_client.get_database(self.DATABASE_NAME)
        if ontology not in self.known_ontologies:
            raise ValueError(f"Invalid ontology: {ontology}")
        collection = db.get_collection(ontology)
        match ontology:
            case "snomedct":
                return repository.SnomedCTConceptRepository(collection)
            case "radlex":
                return repository.RadlexConceptRepository(collection)
            case "anatomic_locations":
                return repository.AnatomicLocationRepository(collection)
            case _:
                raise ValueError(f"Invalid ontology: {ontology}")
