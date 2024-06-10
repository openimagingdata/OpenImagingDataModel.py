from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CaseSignificance(StrEnum):
    INSENSITIVE = "insensitive"
    SENSITIVE = "sensitive"
    INITIAL_LETTER = "initial-letter"


class SnomedCTModule(StrEnum):
    SNOMED_CT_CORE = "SNOMED-CT-core"
    SNOMED_CT_MODEL_COMPONENT = "SNOMED-CT-model-component"
    NLM = "NLM"


class SnomedCTConcept(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        coerce_numbers_to_str=True,
        alias_generator=to_camel,
        validate_assignment=True,
    )
    concept_id: str
    effective_date: date
    modules: list[SnomedCTModule]
    embedding_vector: list[float] | None = None
    language_code: str
    preferred_term: str
    terms: list[str]
    case_significance: CaseSignificance
    definitions: list[str] | None = None

    
    def text_for_embedding(self):
        """ Combine preferred term, alternate terms, 
            and definition into a single text string.
        """
        # Combine the terms and definition into a single string
        # Alternate terms are joined by a comma and a space
        text_components = []
        
        # Add the preferred term if it exists
        if self.preferred_term:
            text_components.append(self.preferred_term)
        
        if self.terms:
            text_components.append(', '.join(self.terms))

        if self.definitions:
            text_components.append(' '.join(self.definitions))
        
        # Combine the available fields into a single string for embedding
        combined_text = ', '.join(text_components)
        if combined_text: 
            return combined_text