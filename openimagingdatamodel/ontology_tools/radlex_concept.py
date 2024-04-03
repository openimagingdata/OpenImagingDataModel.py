import caseswitcher
from pydantic import BaseModel, ConfigDict, field_validator

# Define RadLexProperties dictionary to account for "http://radlex" field
RadLexProperties = dict[str, str | list[str]]


# ConfigDict for RadLex Properties
class RadLexConcept(BaseModel):
    model_config = ConfigDict(populate_by_name=True, coerce_numbers_to_str=True)

    # Define the new document format and fields
    id: str
    preferred_label: str
    synonyms: list[str] | None = None
    parent: str | None = None
    definition: str | None = None
    radlex_properties: RadLexProperties

    # Field validator for model_config dictionary keys
    @field_validator("radlex_properties", mode="before")
    def convert_model_config_keys(cls, value):
        if isinstance(value, dict):
            snake_case_config = {}
            for key, val in value.items():
                snake_case_config[caseswitcher.to_snake(key)] = val
            return snake_case_config
        return value
