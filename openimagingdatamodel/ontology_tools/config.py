from os import getenv

import lancedb
import openai
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from . import repository


class Config:
    def __init__(
        self,
        dotenv_path: str = ".env",
        openai_api_key: str | None = None,
        mongo_dsn: str | None = None,
        database_name: str | None = None,
    ):
        if dotenv_path:
            load_dotenv(dotenv_path)

        self.OPENAI_API_KEY = openai_api_key or getenv("OPENAI_API_KEY")
        if not self.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found in environment or .env file (OPENAI_API_KEY).")
        openai.api_key = self.OPENAI_API_KEY
        self.MONGO_DSN = mongo_dsn or getenv("MONGO_DSN")
        if not self.MONGO_DSN:
            raise ValueError("MongoDB DSN not found in environment or .env file (MONGO_DSN).")
        self.DATABASE_NAME = database_name or getenv("DATABASE_NAME") or "ontologies"

        self._KNOWN_ONTOLOGIES = ("snomedct", "radlex", "anatomic_locations")

        self.LANCEDB_API_KEY = getenv("LANCEDB_API_KEY")
        if not self.LANCEDB_API_KEY:
            raise ValueError("LanceDB API key not found in environment or .env file (LANCEDB_API_KEY).")
        self.LANCEDB_URI = getenv("LANCEDB_URI")
        if not self.LANCEDB_URI:
            raise ValueError("LanceDB URL not found in environment or .env file (LANCEDB_URI).")
        self.LANCEDB_REGION = getenv("LANCEDB_REGION")
        if not self.LANCEDB_REGION:
            raise ValueError("LanceDB region not found in environment or .env file (LANCEDB_REGION).")

        self._async_llm: openai.AsyncOpenAI | None = None
        self._async_db_client: AsyncIOMotorClient | None = None
        self._lancedb_conn: lancedb.AsyncConnection | None = None

    @property
    def llm(self) -> openai.AsyncOpenAI:
        if self._async_llm is None:
            self._async_llm = openai.AsyncOpenAI(api_key=self.OPENAI_API_KEY)
        return self._async_llm

    @property
    def db_client(self) -> AsyncIOMotorClient:
        if self._async_db_client is None:
            self._async_db_client = AsyncIOMotorClient(self.MONGO_DSN)
        return self._async_db_client

    @property
    async def lancedb_conn(self) -> lancedb.AsyncConnection:
        if self._lancedb_conn is None:
            self._lancedb_conn = await lancedb.connect_async(
                uri=self.LANCEDB_URI, api_key=self.LANCEDB_API_KEY, region=self.LANCEDB_REGION
            )
        return self._lancedb_conn

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


settings = Config()
