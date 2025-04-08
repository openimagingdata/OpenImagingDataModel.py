import asyncio
from pprint import pprint

from .config import settings
from .search import llm_filter_results, search_one


async def main():
    search_results = []
    for ontology in settings.known_ontologies:
        repository = settings.get_repository(ontology)
        count  = await repository.get_count()
        print(f"Ontology: {ontology}: {count} items")
        results = await search_one(ontology, "brain")
        search_results.extend(results)
        print(f" - {ontology}: {len(results)} results")
    
    print("Filtering results...")
    targeted_results, related_results = await llm_filter_results(search_results, "brain")
    print("Targeted results:")
    pprint(targeted_results)
    print("Related results:")
    pprint(related_results)



if __name__ == "__main__":
    print("OIDM Ontology Tools")
    asyncio.run(main())
