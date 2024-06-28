import pandas as pd
import streamlit as st
from openimagingdatamodel.ontology_tools.config import Config

st.set_page_config(page_title="OpenImagingDataModel", page_icon=":brain:")


@st.cache_resource
def get_config() -> Config:
    return Config()

def ping_database(config: Config) -> str:
    client = config.db_client
    db = client.get_database(config.DATABASE_NAME)
    return str(db.command("ping"))


def ping_openai(config: Config) -> str:
    llm = config.llm
    result = llm.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Ready?"}])
    return result.choices[0].message.content

def tabulate_search_results(text_search_results, vector_search_results, existing_table = None):
    VECTOR_SCORE_SCALE = 20
    table = [
        [result.system, result.code, result.display, result.score, 0]
        for result in text_search_results
    ]
    for result in vector_search_results:
        needs_own_row = True
        for row in table:
            system, code = row[0], row[1]
            if result.system == system and result.code == code:
                row[4] = result.score
                needs_own_row = False
                break
        if needs_own_row:
            table.append([result.system, result.code, result.display, 0, result.score])
    for row in table:
        text_score, vector_score = row[3], row[4]
        total_score = (text_score * text_score + VECTOR_SCORE_SCALE * VECTOR_SCORE_SCALE * vector_score * vector_score)**0.5
        row.append(total_score)
    if existing_table:
        table.extend(existing_table)
    table = sorted(table, key=lambda x: x[5], reverse=True)
    return table


st.logo(image="frontend/images/oidmlogo.png", icon_image="frontend/images/oidmicon.png")
col1, col2 = st.columns([2, 1])
col2.image("frontend/images/oidmlogo.png", width=250)
col1.title("Hello, Ontologies!")

config = get_config()
radlex_repo = config.get_repository("radlex")
snomedct_repo = config.get_repository("snomedct")
anatomic_locations_repo = config.get_repository("anatomic_locations")

with st.form("search_form"):
    query = st.text_input("Search term")
    col1, col2, col3 = st.columns(3)
    use_anatomic_locations = col1.checkbox("Anatomic Locations") 
    use_radlex = col2.checkbox("RadLex")
    use_snomedct = col3.checkbox("SNOMED-CT")
    col1, col2 = st.columns([3, 1])
    count = col1.select_slider("Results/ontology", options=[5, 10, 15, 20])
    submitted = col2.form_submit_button("Search")

status_box = st.empty()
table_box = st.empty()
if submitted:
    count = int(count) # type: ignore
    table_box.empty()
    concept_table: list[list] = []
    query_vector = config.embedder.create_embedding_for_text(query)
    if use_radlex:
        with status_box.status("Searching RadLex", ) as status:
            text_results  = radlex_repo.text_search(query, count)
            vector_results = radlex_repo.vector_search(query_vector, count)
        concept_table = tabulate_search_results(text_results, vector_results, concept_table)
        table_box.table(concept_table)
    if use_anatomic_locations:
        with status_box.status("Searching Anatomic Locations", ) as status:
            text_results  = anatomic_locations_repo.text_search(query, count)
            vector_results = anatomic_locations_repo.vector_search(query_vector, count)
        concept_table = tabulate_search_results(text_results, vector_results, concept_table)
        status_box.empty()
        table_box.table(concept_table)
    if use_snomedct:
        with status_box.status("Searching SNOMED CT", ) as status:
            text_results  = snomedct_repo.text_search(query, count)
            vector_results = snomedct_repo.vector_search(query_vector, count)
        concept_table = tabulate_search_results(text_results, vector_results, concept_table)
        status_box.empty()
        table_box.table(concept_table)