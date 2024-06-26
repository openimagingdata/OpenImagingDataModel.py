from typing import Literal, Union

from pydantic import BaseModel, Field

from .common import (
    Contributors,
    Event,
    Image,
    IndexCode,
    Reference,
    SchemaVersion,
    Specialty,
    Status,
    Version,
)


class BaseElement(BaseModel):
    id: str = Field(pattern="^(RDE|TO_BE_DETERMINED)\d+")
    parent_set: str | None = Field(default=None, pattern="^(RDES|TO_BE_DETERMINED)\d+")
    name: str
    definition: str | None = None
    question: str | None = None
    element_version: Version
    schema_version: SchemaVersion
    status: Status
    index_codes: list[IndexCode] | None = None
    contributors: Contributors | None = None
    history: list[Event] | None = None
    specialties: list[Specialty] | None = None
    references: list[Reference] | None = None
    source: str | None = None


class ValueSetValue(BaseModel):
    code: str = Field(pattern="^(RDE|TO_BE_DETERMINED)\d+\.\d+")
    value: str | None = None
    name: str
    definition: str | None = None
    index_codes: list[IndexCode] | None = None
    images: list[Image] | None = None


class ValueSet(BaseModel):
    min_cardinality: int  # TODO: Minimum value is 0
    max_cardinality: int | None = None
    values: list[ValueSetValue]  # TODO: Minimum length is 2


class ValueSetElement(BaseElement):
    value_set: ValueSet

    def get_value(self, val: str) -> ValueSetValue:
        """Get a ValueSetValue by code or value or name."""
        if not hasattr(self, "_value_index"):
            self._value_index = {}
            for v in self.value_set.values:
                self._value_index[v.code.casefold()] = v
                self._value_index[v.value.casefold()] = v
                self._value_index[v.name.casefold()] = v
        if val.casefold() in self._value_index:
            return self._value_index[val.casefold()]
        raise ValueError(f"Value '{v}' not found in ValueSet")


# This corresponds to the floatElementSchema class in the cdElement.ts file
class FloatValue(BaseModel):
    min: float | None = None
    max: float | None = None
    step: float | None = None
    unit: str | None = None


class FloatElement(BaseElement):
    float_value: FloatValue


class IntegerValue(BaseModel):
    min: int | None = None
    max: int | None = None
    step: int | None = None
    unit: str | None = None


class IntegerElement(BaseElement):
    integer_value: IntegerValue


# This corresponds to the booleanElementSchema class in the cdElement.ts file
class BooleanElement(BaseElement):
    boolean_value: Literal["boolean"]


# Define a type CDElement which can be either a ValueSetElement, FloatElement, IntegerElement or BooleanElement
CDEElement = Union[ValueSetElement, FloatElement, IntegerElement, BooleanElement]
