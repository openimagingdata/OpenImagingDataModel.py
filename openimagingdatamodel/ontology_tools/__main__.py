import asyncio
import sys
import time
from pprint import pprint

from .config import Config
from .search import SEARCH_TYPES, async_search  # , search


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
            progress = f"{i + 1} - {i + batch_size} / {total_concepts}"
            print(f"Successfully embedded {len(batch)} concepts ({progress}; {batch_time:.2f}s).")
        else:
            print("Error: Failed to write embedding vectors.")
            sys.exit(1)
    print(f"Total time: {time.time() - total_start_time:.2f}s")


if __name__ == "__main__":
    print("OIDM Ontology Tools")
    # See if the first command line argument is one of the commands: "search" or "embed"
    if len(sys.argv) > 1:
        if sys.argv[1] == "search":
            if len(sys.argv) < 6:
                print("Please provide an ontology, a search type, a count, and a query.")
                sys.exit(1)
            config = Config()
            if (ontology := sys.argv[2]) not in config.known_ontologies and ontology != "all":
                print("Invalid ontology. Please use one of: 'snomedct', 'radlex', 'anatomic_locations'.")
                sys.exit(1)
            if (search_type := sys.argv[3]) not in SEARCH_TYPES:
                print("Invalid search type. Please use one of: 'text', 'vector', 'all'.")
                sys.exit(1)
            if not (count := int(sys.argv[4].strip())) > 0:
                print("Invalid count. Please provide a positive integer.")
                sys.exit(1)
            query = " ".join(sys.argv[5:])
            start_time = time.time()
            print("Searching...")
            # results = search(config, ontology, search_type, query, count)
            results = asyncio.run(async_search(config, ontology, search_type, query, count))
            for result in results:
                pprint(result.model_dump())
            print(f"Search time: {time.time() - start_time:.2f}s")
        elif sys.argv[1] == "embed":
            embed(*sys.argv[2:])
        else:
            print("Invalid command. Please use either 'search' or 'embed'.")
    else:
        print("Available commands: 'search', 'embed'")
