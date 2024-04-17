from typing import Any, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field


class Identifier(BaseModel):
    system: str  # TODO: Use URI type
    value: str
    # Can add type (CodeableConcept), use (Code), period (Period), assigner (Reference)


class Coding(BaseModel):
    """COding with system and code.
    Note that the FHIR spec has all fields optional, but we require system and code."""

    system: str  # TODO: Use URI type
    code: str
    version: str | None = None
    display: str | None = None
    user_selected: bool | None = Field(default=None, alias="userSelected")


class CodeableConcept(BaseModel):
    codings: list[Coding] | None = Field(default=None, alias="coding")
    text: str | None = None


StatusValue = Literal[
    "registered", "preliminary", "final", "amended", "corrected", "cancelled", "entered-in-error", "unknown"
]


class Reference(BaseModel):
    reference: str
    type: str | None = None  # TODO: Use URI type and limit to the FHIR reference types
    identifier: Identifier | None = None
    display: str | None = None


class CodeableConceptComponent(BaseModel):
    code: CodeableConcept
    value_codeable_concept: CodeableConcept = Field(alias="valueCodeableConcept")


class StringComponent(BaseModel):
    code: CodeableConcept
    value_string: str = Field(alias="valueString")


class IntegerComponent(BaseModel):
    code: CodeableConcept
    value_integer: int = Field(alias="valueInteger")


class BooleanComponent(BaseModel):
    code: CodeableConcept
    value_boolean: bool = Field(alias="valueBoolean")


# This is a union of all possible component types
Component = CodeableConceptComponent | StringComponent | IntegerComponent | BooleanComponent


class Observation(BaseModel):
    """
    The Observation class is the model for FHIR Observation objects
    """

    model_config = ConfigDict(populate_by_name=True)

    resourceType: Literal["Observation"] = "Observation"
    id_: str = Field(alias="id")
    identifiers: list[Identifier] | None = Field(default=None, alias="identifier")
    status: StatusValue
    subject: Reference | None = None
    focus: list[Mapping[str, Any]] | None = None
    derived_from: list[Reference] | None = Field(default=None, alias="derivedFrom")
    body_site: CodeableConcept | None = Field(default=None, alias="bodySite")
    components: list[Component] | None = Field(default=None, alias="component")
