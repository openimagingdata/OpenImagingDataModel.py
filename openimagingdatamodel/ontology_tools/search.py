from typing import Literal

import instructor
from openai import OpenAI
from pydantic import BaseModel

from .config import settings
from .search_result import SearchResult


async def search_one(system: str, query: str, count: int = 20) -> list[SearchResult]:
    db_conn = await settings.lancedb_conn
    table = await db_conn.open_table(system.lower())
    query_obj = await table.search(query, query_type="hybrid", vector_column_name="vector", fts_columns="concept_text")
    raw_results = await (
        query_obj.select(["concept_id", "concept_text"])
        .limit(count)
        .to_list()
    )

    # r["concept_id"], r["concept_text"], r["_relevance_score"]
    results = [
        SearchResult(
            system=system.upper(),
            code=result["concept_id"],
            display=result["concept_text"],
            score=result["_relevance_score"],
        )
        for result in raw_results
    ]
    return results


async def search(ontology: str, query: str, count: int = 25) -> list[SearchResult]:
    # if search_type not in SEARCH_TYPES:
    #     raise ValueError(f"Invalid search type: {search_type}")
    # if ontology not in config.known_ontologies and ontology != "all":
    #     raise ValueError(f"Invalid ontology: {ontology}")
    # if not (query := query.strip()) or len(query) < 3:
    #     raise ValueError("Query must not be empty or less than 3 characters.")
    ...


class SelectedResult(BaseModel):
    system: Literal["SNOMEDCT", "RADLEX", "ANATOMICLOCATIONS"]
    code: str
    display: str


async def llm_filter_results(results: list[SearchResult], query: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    query = query.strip()

    instructor_llm = instructor.from_openai(settings.llm)

    prompt = f"Filter the following results based whether these are actual matches for the query: '{query}'\n\n"
    for result in results:
        prompt += f"{result.short_string()}\n"

    system_message = {
        "role": "system",
        "content": "You are an expert in medical terminology who can determine which codes from standard"
        + " ontologies are identical or related to a given query.",
    }

    filtered_results = await instructor_llm.chat.completions.create(
        model="gpt-4o-mini",
        response_model=list[SelectedResult],
        messages=[system_message, {"role": "user", "content": prompt}],  # type: ignore
    )

    prompt = f"Filter the following results based whether these are not matches, but rather concepts related to the query: '{query}'\n\n"  # noqa: E501
    for result in results:
        prompt += f"{result.short_string()}\n"

    related_results = await instructor_llm.chat.completions.create(
        model="gpt-4o",
        response_model=list[SelectedResult],
        messages=[system_message, {"role": "user", "content": prompt}],  # type: ignore
    )

    return ([result.model_dump() for result in filtered_results], [result.model_dump() for result in related_results])
