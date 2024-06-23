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


st.title("Hello, OpenImagingDataModel!")

config = get_config()
with st.spinner("Connecting to MongoDB and OpenAI..."):
    db_status = ping_database(config)
    st.toast(f"Connected to MongoDB: `{db_status}`")
    llm_status = ping_openai(config)
    st.toast(f"Connected to OpenAI: `{llm_status}`")

radlex_repo = config.get_repository("radlex")
st.write("RadLex concepts count:", radlex_repo.get_count())
concepts = radlex_repo.get_random_concepts(5)
for concept in concepts:
    st.write(concept.text_for_embedding())
concept = radlex_repo.get_concept("RID35145")
st.write(f"Concept {concept.id}: {concept.preferred_label}")