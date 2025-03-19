    from typing import Literal, Union

    from pydantic import BaseModel, Field

    from .common import (
        BodyPart,
        Contributors,
        Event,
        Image,
        IndexCode,
        Modality,
        Reference,
        SchemaVersion,
        Specialty,
        Status,
        Version,
    )


    #"required": ["id", "name", "element_version", "status", "schema_version"]
    class BaseElement(BaseModel):
        id: str = Field(
            pattern=r"^(RDE|TO_BE_DETERMINED)\d+",
            max_length=100,
            description="The TO_BE_DETERMINED123 pattern is used for author convenience and tracking during the authoring process. Upon submission to the radelement archive an element number will be assigned and used for all further references overwriting this value", 
            examples: ["RDES42", "RDES1042"]
        )
        parent_set: Optional[str] = Field(
            default=None,
            pattern=r"^(RDES|TO_BE_DETERMINED)\d+",
            description="The parent set of the element. This is the set that the element belongs to. If the element is not part of a set, this value should be TO_BE_DETERMINED.",
            examples: ["RDES42", "RDES1042"]
        )
        name: str
        definition: str = Field(..., description= "A human readable definition explaining the clinical context of the data element", max_length=100)
        question: Optional[str] = Field(default=None, description="How a user might be prompted to provide a value")
        element_version: Version
        schema_version: Literal["1.0.0"]
        status: Status
        url: Optional[HttpUrl] = Field(default=None)
        index_codes: Optional[list[IndexCode]] = Field(default=None)
        contributors: Optional[Contributors] = Field(default=None)
        history: Optional[list[Event]] = Field(default=None)
        specialty: Optional[list[Specialty]] = Field(default=None)
        references: Optional[list[Reference]] = Field(default=None)


    # V 1.1.0"required": ["id", "name", "element_version", "current_status", "schema_version"],

    class BaseElement11(BaseModel):
        id: str = Field(
            pattern=r"^(RDE|TO_BE_DETERMINED)\d+",
            max_length=100,
            description="The TO_BE_DETERMINED123 pattern is used for author convenience and tracking during the authoring process. Upon submission to the radelement archive, an element number will be assigned and used for all further references, overwriting this value", 
            examples=["RDES42", "RDES1042"]
        )
        parent_set: Optional[str] = Field(
            default=None,
            pattern=r"^(RDES|TO_BE_DETERMINED)\d+",
            description= "The TO_BE_DETERMINED123 pattern is used for author convenience and tracking during the authoring process. Upon submission to the radelement archive RDES will be assigned and used for all further references overwriting this value",
            examples=["RDES42", "RDES1042"]
        )
        name: str = Field(..., description="Element names consistent with https://rsna.github.io/ACR-RSNA-CDEs/reference/element/")
        definition: str = Field(..., description="A human-readable definition explaining the clinical context of the data element", max_length=100)
        question: Optional[str] = Field(default=None, description="How a user might be prompted to provide a value")
        element_version: Version
        schema_version: Literal["1.1.0"]
        current_status: Status
        index_codes: Optional[List[IndexCode]] = Field(default=None)
        body_parts: Optional[List[BodyPart]] = Field(default=None)
        modalities: Optional[List[Modality]] = Field(default=None)
        contributors: Optional[Contributors] = Field(default=None)
        history: Optional[List[Status]] = Field(default=None)
        specialty: Optional[List[Specialty]] = Field(default=None)
        images: Optional[List[Image]] = Field(default=None)
        references: Optional[List[Reference]] = Field(default=None)

        class Config:
            min_anystr_length = 1
            anystr_strip_whitespace = True


    class ValueSetValue(BaseModel):
        code: str = Field(pattern=r"^(RDE|TO_BE_DETERMINED)\d+\.\d+")
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
                    if v.value:
                        self._value_index[v.value.casefold()] = v
                    self._value_index[v.name.casefold()] = v
            if val.casefold() in self._value_index:
                return self._value_index[val.casefold()]
            raise ValueError(f"Value '{val}' not found in ValueSet")


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
