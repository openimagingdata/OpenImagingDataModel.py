import asyncio
from typing import Literal

import instructor
from openai import OpenAI
from pydantic import BaseModel

from . import repository
from .config import Config
from .embedding_creator import EmbeddingCreator
from .search_result import SearchResult

SEARCH_TYPES = ("text", "vector", "all")


def normalize_results(results: list[SearchResult]) -> list[SearchResult]:
    min_score = min(result.score for result in results)
    max_score = max(result.score for result in results)
    score_range = max_score - min_score
    return [
        SearchResult(
            system=result.system,
            code=result.code,
            display=result.display,
            score=(result.score - min_score) / score_range,
        )
        for result in results
    ]


def search_one(
    repo: repository.Repository,
    search_type: str,
    query: str,
    count: int,
    embedder: EmbeddingCreator | None = None,
    normalize: bool = True,
) -> list[SearchResult]:
    assert search_type in SEARCH_TYPES, f"Invalid search type: {search_type}"
    results = []
    if search_type in ["vector", "all"]:
        if embedder is None:
            raise ValueError("Embedder required for vector search.")
        query_vector = embedder.create_embedding_for_text(query)
        vector_results = repo.vector_search(query_vector, count)
        if normalize:
            vector_results = normalize_results(vector_results)
        results.extend(vector_results)
    if search_type in ["text", "all"]:
        text_results = repo.text_search(query, count)
        if normalize:
            text_results = normalize_results(text_results)
        results.extend(text_results)
    return results


async def async_search_one(
    repo: repository.AsyncRepository,
    search_type: str,
    query: str,
    count: int,
    embedder: EmbeddingCreator | None = None,
    normalize: bool = True,
) -> list[SearchResult]:
    assert embedder is not None or search_type not in ["vector", "all"], "Embedder required for vector search."
    match search_type:
        case "all":
            query_vector = embedder.create_embedding_for_text(query)
            vector_task = repo.vector_search(query_vector, count)
            text_task = repo.text_search(query, count)
            vector_results, text_results = await asyncio.gather(vector_task, text_task)
            if normalize:
                vector_results = normalize_results(vector_results)
                text_results = normalize_results(text_results)
            return vector_results + text_results
        case "vector":
            query_vector = embedder.create_embedding_for_text(query)
            vector_results = await repo.vector_search(query_vector, count)
            return normalize_results(vector_results) if normalize else vector_results
        case "text":
            text_results = await repo.text_search(query, count)
            return normalize_results(text_results) if normalize else text_results
        case _:
            raise ValueError(f"Invalid search type: {search_type}")


def search(
    config: Config, ontology: str, search_type: str, query: str, count: int = 25, normalize: bool = True
) -> list[SearchResult]:
    if search_type not in SEARCH_TYPES:
        raise ValueError(f"Invalid search type: {search_type}")
    if ontology not in config.known_ontologies and ontology != "all":
        raise ValueError(f"Invalid ontology: {ontology}")
    if not (query := query.strip()) or len(query) < 3:
        raise ValueError("Query must not be empty or less than 3 characters.")

    embedder = config.embedder if search_type in ["vector", "all"] else None

    if ontology == "all":
        results = []
        for ontology in config.known_ontologies:
            repo = config.get_repository(ontology)
            results.extend(search_one(repo, search_type, query, count, embedder))
        return results

    repo = config.get_repository(ontology)
    results = search_one(repo, search_type, query, count, embedder)
    if normalize:
        results = normalize_results(results)
    return results


async def async_search(
    config: Config, ontology: str, search_type: str, query: str, count: int = 25, normalize: bool = True
) -> list[SearchResult]:
    if search_type not in SEARCH_TYPES:
        raise ValueError(f"Invalid search type: {search_type}")
    if ontology not in config.known_ontologies and ontology != "all":
        raise ValueError(f"Invalid ontology: {ontology}")
    if not (query := query.strip()) or len(query) < 3:
        raise ValueError("Query must not be empty or less than 3 characters.")

    embedder = config.embedder if search_type in ["vector", "all"] else None

    if ontology == "all":
        tasks = [
            async_search_one(config.get_async_repository(ontology), search_type, query, count, embedder)
            for ontology in config.known_ontologies
        ]
        ontology_results: list[list[SearchResult]] = await asyncio.gather(*tasks)
        return [result for results in ontology_results for result in results]

    results = await async_search_one(config.get_async_repository(ontology), search_type, query, count, embedder)
    if normalize:
        results = normalize_results(results)
    return results


class SelectedResult(BaseModel):
    system: Literal["SNOMEDCT", "RADLEX", "ANATOMICLOCATIONS"]
    code: str
    display: str


def llm_filter_results(
    llm: OpenAI, results: list[SearchResult], query: str
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    query = query.strip()

    instructor_llm = instructor.from_openai(llm)

    prompt = f"Filter the following results based whether these are actual matches for the query: '{query}'\n\n"
    for result in results:
        prompt += f"{result.short_string()}\n"

    system_message = {
        "role": "system",
        "content": "You are an expert in medical terminology who can determine which codes from standard"
        + " ontologies are identical or related to a given query.",
    }

    filtered_results = instructor_llm.chat.completions.create(
        model="gpt-4o",
        response_model=list[SelectedResult],
        messages=[system_message, {"role": "user", "content": prompt}],  # type: ignore
    )

    prompt = f"Filter the following results based whether these are not matches, but rather concepts related to the query: '{query}'\n\n"
    for result in results:
        prompt += f"{result.short_string()}\n"

    related_results = instructor_llm.chat.completions.create(
        model="gpt-4o",
        response_model=list[SelectedResult],
        messages=[system_message, {"role": "user", "content": prompt}],  # type: ignore
    )

    return ([result.model_dump() for result in filtered_results], 
        [result.model_dump() for result in related_results])
