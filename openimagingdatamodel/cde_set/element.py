from typing import Literal, Union

from pydantic import BaseModel

from .common import Contributors, Event, Image, IndexCode, Reference, Specialty, Status, Version


class BaseElement(BaseModel):
    id: str
    parent_set: str | None = None  # TODO: add formatting for a Set ID
    name: str
    definition: str | None = None
    question: str | None = None
    version: Version
    status: Status
    index_codes: list[IndexCode] | None = None
    contributors: Contributors | None = None
    history: list[Event] | None = None
    specialty: list[Specialty] | None = None
    references: list[Reference] | None = None
    source: str | None = None


class ValueSetValue(BaseModel):
    code: str  # TODO: Add regex for code
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
