from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class SnomedCTConcept(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        coerce_numbers_to_str=True,
        alias_generator=to_camel,
        validate_assignment=True,
    )
    concept_id: str
    effective_date: str
    modules: list[str]
    language_code = str
    preferred_term = str
    terms = list[str]
    case_significance = str
    definitions = list[str]
