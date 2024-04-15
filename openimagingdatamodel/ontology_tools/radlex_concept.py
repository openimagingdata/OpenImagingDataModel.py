from typing import Sequence

import caseswitcher
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from pydantic.alias_generators import to_camel

# Define RadLexProperties dictionary to account for "http://radlex" field
RadLexProperties = dict[str, str | Sequence[str]]


# ConfigDict for RadLex Properties
class RadLexConcept(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        coerce_numbers_to_str=True,
        alias_generator=to_camel,
        validate_assignment=True,
    )

    # Define the new document format and fields
    id: str = Field(alias="_id")
    preferred_label: str
    synonyms: list[str] | None = None
    parent: str | None = None
    definition: str | None = None
    radlex_properties: RadLexProperties | None = None

    # Field validator for radlex property dictionary keys
    @field_validator("radlex_properties", mode="before")
    def radlex_property_keys_to_snake(cls, value):
        if isinstance(value, dict):
            out_properties = {}
            for key, val in value.items():
                out_properties[caseswitcher.to_snake(key)] = val
            return out_properties
        return value

    # Field serializer to convert radlex property dictionary keys back to camel case
    @field_serializer("radlex_properties", when_used="unless-none")
    def radlex_property_keys_to_camel(self, in_props: RadLexProperties) -> RadLexProperties:
        out_props = {caseswitcher.to_camel(k): v for k, v in in_props.items()}
        return out_props


# class RadLexConceptRepo(db)
