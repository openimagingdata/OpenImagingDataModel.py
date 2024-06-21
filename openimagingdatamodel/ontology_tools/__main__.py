import sys
import time
from pprint import pprint
from typing import Annotated, Literal, Type

from dotenv import dotenv_values
from pydantic import Field, validate_call

from . import repository
from .embedding_creator import EmbeddingCreator


class Config:
    def __init__(self):
        from openai import OpenAI
        from pymongo import MongoClient

        self.config = dotenv_values(".env")
        self.llm = OpenAI(api_key=self.config["OPENAI_API_KEY"])
        self.client = MongoClient(self.config["ATLAS_DSN"])
        self.embedder = EmbeddingCreator(self.llm)

    @validate_call
    def get_repository(self, ontology: Literal["snomedct", "radlex", "anatomic_locations"]) -> repository.Repository:
        collection = self.client["ontologies"][ontology]
        repo_classes: dict[str, Type[repository.Repository]] = {
            "snomedct": repository.SnomedCTConceptRepository,
            "radlex": repository.RadlexConceptRepository,
            "anatomic_locations": repository.AnatomicLocationRepository,
        }
        return repo_classes[ontology](collection)

    def get_all_repositories(self) -> dict[str, repository.Repository]:
        return {
            "snomedct": self.get_repository("snomedct"),
            "radlex": self.get_repository("radlex"),
            "anatomic_locations": self.get_repository("anatomic_locations"),
        }


def search_one(
    repo: repository.Repository,
    type: Literal["text", "vector", "all"],
    query: str,
    embedder: EmbeddingCreator,
):
    results = []
    if type in ["text", "all"]:
        print("Searching text...")
        results.extend(repo.text_search(query, 25))
    if type in ["vector", "all"]:
        print("Searching vectors...")
        query_vector = embedder.create_embedding_for_text(query)
        results.extend(repo.vector_search(query_vector, 25))
    return results


def search_all(
    repositories: dict[str, repository.Repository],
    type: Literal["text", "vector", "all"],
    query: str,
    embedder: EmbeddingCreator,
):
    results = []
    for ontology, repo in repositories.items():
        print(f"Searching {ontology}...")
        results.extend(search_one(repo, type, query, embedder))
    return results


def print_search_results(results):
    for result in results:
        pprint(result.model_dump())


@validate_call
def search(
    ontology: Literal["snomedct", "radlex", "anatomic_locations", "all"],
    type: Literal["text", "vector", "all"],
    query: Annotated[str, Field(min_length=3)],
):
    print(f"Search function called with arguments: {ontology=}, {type=}, {query=}")
    config = Config()

    if ontology == "all":
        repositories = config.get_all_repositories()
        results = search_all(repositories, type, query, config.embedder)
        print_search_results(results)
        return

    repo = config.get_repository(ontology)
    results = search_one(repo, type, query, config.embedder)
    print_search_results(results)


def embed(*args):
    if len(args) != 3:
        print("Please give the concept name, the total number of concepts, and the batch size.")
        sys.exit(1)
    concept_name, total_concepts, batch_size = args[0], int(args[1]), int(args[2])
    if concept_name not in ["snomedct", "radlex", "anatomic_locations"]:
        print("Invalid concept name. Please use one of: 'snomedct', 'radlex', 'anatomic_locations'.")
        sys.exit(1)

    config = Config()
    embedding_creator = config.embedder
    repo = config.get_repository(concept_name)

    concepts = repo.get_unembedded_concepts(total_concepts)
    print(f"Found {len(concepts)} unembedded concepts.")
    total_start_time = time.time()
    for i in range(0, len(concepts), batch_size):
        batch = concepts[i : i + batch_size]
        vectors = embedding_creator.create_embeddings_for_concepts(batch)
        if len(vectors) != len(batch) or not all(len(v) == 1536 for v in vectors):
            print("Error: Some vectors are missing or have the wrong length.")
            sys.exit(1)
        start_time = time.time()
        result = repo.write_embedding_vectors(batch, vectors)
        batch_time = time.time() - start_time
        if result:
            print(
                f"Successfully embedded {len(batch)} concepts ({i + 1} - {i + batch_size} / {total_concepts}; {batch_time:.2f}s)."
            )
        else:
            print("Error: Failed to write embedding vectors.")
            sys.exit(1)
    print(f"Total time: {time.time() - total_start_time:.2f}s")


if __name__ == "__main__":
    print("OIDM Ontology Tools")
    # See if the first command line argument is one of the commands: "search" or "embed"
    if len(sys.argv) > 1:
        if sys.argv[1] == "search":
            search(sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]))
        elif sys.argv[1] == "embed":
            embed(*sys.argv[2:])
        else:
            print("Invalid command. Please use either 'search' or 'embed'.")
    else:
        print("Available commands: 'search', 'embed'")
