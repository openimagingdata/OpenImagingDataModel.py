# TODO for OpenImagingDataModel.py

## Testing

- Get tests going similar using `pytest` similar to those used for `OpenImagingDataModel.ts`
- Make sure to cover the functionality in `notebooks/observation_factory_demo.ipynb` and `notebooks/set_factory_demo.ipynb` especially because we will be using these a lot
- `FindingModel` is also important to make sure we have basic tests for

## Tooling

- Switch from [poetry](https://python-poetry.org) to [uv](https://docs.astral.sh/uv/)
- Make sure main dev tools ([ruff](https://docs.astral.sh/ruff/), [mypy](https://www.mypy-lang.org/)) are using updated versions
- Switch from using the poetry-based poe-the-poet task runner to [task](https://taskfile.dev) and make the new `Taskfile.toml` to take in the tasks there
- Update versions of dependencies

## `ontology_tools`

- We need to update the existing `Repository`/`AsyncRepository` classes to use the LanceDB index instead of MongoDB Atlas facilities or mongo-based vector searching.
  - Pull out all of the code in `Repository` that does the embedding work
  - Do we still want both synchronous and asynchronous versions? Wouldn't just one asyncrhonous version be better?
  - Instead of searching using the mongodb, use the LanceDB connection to do the hybrid search ± reranking with OpenAI:

```python
import lancedb

db_conn = lancedb.connect(uri=env["LANCEDB_URI"], api_key=env["LANCEDB_API_KEY"])
db_conn.table_names()
# ['anatomic_locations', 'radlex', 'snomedct']

radlex = db_conn.open_table("radlex")
# RemoteTable(cdetools-w5qh9c.radlex)
radlex.count_rows()
# 46761

results = radlex.(
    radlex.search("posterior cruciate ligament tear", query_type="hybrid", vector_column_name="vector")
    .to_list()
)
[(r["concept_id"], r["concept_text"], r["_relevance_score"]) for r in results]
# [('RID2784',
#   'posterior cruciate ligament\n: A strong ligament of the knee that originates from the anterolateral surface of the medial condyle of the femur, passes posteriorly and inferiorly between the condyles, and attaches to the posterior intercondylar area of the tibia. [MeSH] (synonyms: ligamentum cruciatum posterius; Hinteres Kreuzband)',
#   1.0),
#  ('RID48250',
#   'posteromedial band of left posterior cruciate ligament',
#   0.8999999761581421),
#  ('RID48249',
#   'posteromedial band of right posterior cruciate ligament',
#   0.8999999761581421),
#   ...
# ]

# With reranker
from lancedb.rerankers import OpenaiReranker

reranker = OpenaiReranker(model_name="o1-mini")
results = radlex.(
    radlex.search("posterior cruciate ligament tear", query_type="hybrid", vector_column_name="vector")
    .rerank(reranker)
    .to_list()
)
# Takes a few seconds for OpenAI call...
```