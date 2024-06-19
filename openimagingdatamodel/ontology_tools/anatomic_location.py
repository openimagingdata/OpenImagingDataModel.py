import re
from typing import Annotated, ClassVar, Literal

from annotated_types import MinLen
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from pydantic.alias_generators import to_camel

from .concept import Code as CodedConcept
from .concept import Concept


def check_anatomic_location_id(v: str):
    v = v.strip()
    match = re.match(r"^RID\d{2,}(_RID\d{2,})*$", v)
    if not match:
        raise ValueError("Invalid anatomic location ID")
    return v


def check_numeric_string(v: str):
    v = v.strip()
    match = re.match(r"^\d{3,}$", v)
    if not match:
        raise ValueError("Invalid numeric string")
    return v


def check_compound_numeric_string(v: str):
    v = v.strip()
    match = re.match(r"^\d{3,}(_\d{3,})*$", v)
    if not match:
        raise ValueError("Invalid compound numeric strings")
    return v


AnatomicLocationId = Annotated[str, BeforeValidator(check_anatomic_location_id)]
NumericString = Annotated[str, BeforeValidator(check_numeric_string)]
CompoundNumericString = Annotated[str, BeforeValidator(check_compound_numeric_string)]
NonEmptyString = Annotated[str, MinLen(3)]
Region = Annotated[
    Literal["Body", "Head", "Neck", "Thorax", "Upper Extremity", "Breast", "Abdomen", "Pelvis", "Lower Extremity"],
    BeforeValidator(lambda v: v.title()),
]


class AnatomicLocationRef(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, validate_assignment=True)

    id: AnatomicLocationId
    display: NonEmptyString | None = None


class Code(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, validate_assignment=True)

    system: NonEmptyString
    code: NonEmptyString
    display: NonEmptyString | None = None


# Define a Link class that inherits from BaseModel and has a site field which is a NonEmptyString
# and a url field which is a string which must be a URL
class Link(BaseModel):
    site: NonEmptyString
    url: str = Field(pattern=r"^https?://")


class AnatomicLocation(Concept):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        validate_assignment=True,
    )

    SYSTEM_NAME: ClassVar[str] = "ANATOMICLOCATIONS"

    acr_common_id: NumericString | None = None
    snomed_id: CompoundNumericString | None = None
    snomed_display: NonEmptyString | None = None
    description: NonEmptyString
    definition: NonEmptyString | None = None
    region: Region
    contained_by_ref: AnatomicLocationRef | None = None
    contains_refs: Annotated[list[AnatomicLocationRef], MinLen(1)] | None = None
    synonyms: Annotated[list[str], MinLen(1)] | None = None
    part_of_ref: AnatomicLocationRef | None = None
    has_parts_refs: Annotated[list[AnatomicLocationRef], MinLen(1)] | None = None
    left_ref: AnatomicLocationRef | None = None
    right_ref: AnatomicLocationRef | None = None
    unsided_ref: AnatomicLocationRef | None = None
    sex_specific: Literal["Male", "Female"] | None = None
    codes: Annotated[list[Code], MinLen(1)] | None = None
    links: Annotated[list[Link], MinLen(1)] | None = None

    def text_for_embedding(self) -> str:
        out = self.description
        if self.definition:
            out += f" Definition: {self.definition}"
        if self.synonyms:
            out += f" (synonyms: {'; '.join(self.synonyms)})"
        return out

    def to_system_code_display(self) -> CodedConcept:
        return CodedConcept(self.SYSTEM_NAME, self.id, self.description)
