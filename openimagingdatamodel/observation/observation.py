from typing import Any, Literal, Mapping, TypeAlias

from pydantic import BaseModel, ConfigDict, Field


class Identifier(BaseModel):
    system: str  # TODO: Use URI type
    value: str
    # Can add type (CodeableConcept), use (Code), period (Period), assigner (Reference)


class Coding(BaseModel):
    """Coding with system and code.
    Note that the FHIR spec has all fields optional, but we require system and code."""

    model_config = ConfigDict(populate_by_name=True)
    system: str  # TODO: Use URI type
    code: str
    version: str | None = None
    display: str | None = None
    user_selected: bool | None = Field(default=None, alias="userSelected")


class CodeableConcept(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    codings: list[Coding] = Field(alias="coding", min_length=1)
    text: str | None = None


StatusValue = Literal[
    "registered", "preliminary", "final", "amended", "corrected", "cancelled", "entered-in-error", "unknown"
]


class Reference(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    reference: str
    type: str | None = None  # TODO: Use URI type and limit to the FHIR reference types
    identifier: Identifier | None = None
    display: str | None = None


class CodeableConceptComponent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    code: CodeableConcept
    value_codeable_concept: CodeableConcept = Field(alias="valueCodeableConcept")


class StringComponent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    code: CodeableConcept
    value_string: str = Field(alias="valueString")


class IntegerComponent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    code: CodeableConcept
    value_integer: int = Field(alias="valueInteger")


class BooleanComponent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    code: CodeableConcept
    value_boolean: bool = Field(alias="valueBoolean")


# This is a union of all possible component types
Component: TypeAlias = CodeableConceptComponent | StringComponent | IntegerComponent | BooleanComponent


class Observation(BaseModel):
    """
    The Observation class is the model for FHIR Observation objects
    """

    model_config = ConfigDict(populate_by_name=True)

    resourceType: Literal["Observation"] = "Observation"
    id_: str = Field(alias="id")
    identifiers: list[Identifier] | None = Field(default=None, alias="identifier")
    code: CodeableConcept | None = None
    status: StatusValue
    subject: Reference | None = None
    focus: list[Mapping[str, Any]] | None = None
    body_site: CodeableConcept | None = Field(default=None, alias="bodySite")
    derived_from: list[Reference] | None = Field(default=None, alias="derivedFrom")
    components: list[Component] = Field(default_factory=list, alias="component")

    def add_code_str(self, code: str, system: str, display: str | None = None) -> None:
        coding = Coding(system=system, code=code, display=display)
        self.add_coding(coding)

    def add_coding(self, coding: Coding) -> None:
        if self.code is None:
            self.code = CodeableConcept(coding=[coding])
        else:
            self.code.codings.append(coding)
