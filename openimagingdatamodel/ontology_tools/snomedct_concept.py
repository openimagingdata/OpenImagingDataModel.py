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
    embedding: list[float] | None = None
    language_code: str
    preferred_term: str
    terms: list[str]
    case_significance: CaseSignificance
    definitions: list[str] | None = None
