from dotenv import dotenv_values
from openai import OpenAI
from .snomedct_concept import SnomedCTConcept

async def create_embedding_for_snomedctconcept(concept: SnomedCTConcept) -> SnomedCTConcept:
    # Use OpenAI API to create an embedding vector for the concept
    config = dotenv_values(".env")
    openai_client = OpenAI(api_key=config["OPENAI_EMBEDDING_API_KEY"])
    generated_text = concept.text_for_embedding()
    input_text = generated_text.replace("\n", " ")
    response = openai_client.embeddings.create(input = [input_text], model="text-embedding-3-small")
    concept.embedding_vector = response.data[0].embedding
    return concept
