from pydantic import BaseModel, Field
from typing import List, Optional, Union
from enum import Enum

from cde_set import IndexCode
#class IndexCode(BaseModel):...

class Authors(BaseModel):...

class Event(BaseModel):...

class Specialty(BaseModel):...

class Reference(BaseModel):...

class Version(BaseModel):...

class ValueType(Enum):
    float = 'float'
    valueSet = 'valueSet'
    integer = 'integer'
    boolean = 'boolean'

class BaseElement(BaseModel):
    id: str
    parent_id: int
    name: str
    short_name: Optional[str] = None
    editor: Optional[str] = None
    instructions: Optional[str] = None
    synonyms: Optional[str] = None
    definition: Optional[str] = None
    question: Optional[str] = None
    version: Version
    index_codes: Optional[List[IndexCode]] = None
    authors: Optional[Authors] = None
    history: Optional[List[Event]] = None
    specialty: Optional[List[Specialty]] = None
    references: Optional[List[Reference]] = None
    source: Optional[str] = None

class ValueSetValue(BaseModel):
    value: str
    name: str
    definition: Optional[str] = None
    index_codes: Optional[List[IndexCode]] = None
#To Do: Include images, eventually


# This corresponds to the valueSetElementSchema class in the cdElement.ts file
## Can reuse Cardinality and ValueMinMax for the FloatElement and IntegerElement classes
class Cardinality(BaseModel):
    min_cardinality: int = Field(..., alias='minCardinality')
    max_cardinality: int = Field(..., alias='maxCardinality')

class ValueMinMax(BaseModel):
    value_min: Optional[float] = Field(..., alias='valueMin')
    value_max: Optional[float] = Field(..., alias='valueMax')

class ValueSet(BaseModel):
    value_type: str = Field('valueSet', alias='valueType')
    cardinality: Cardinality
    value_min_max: Optional[ValueMinMax] = Field(None, alias='valueMinMax')
    values: List[ValueSetValue]
    step_value: Optional[float] = Field(None, alias='stepValue')
    unit: Optional[str]
    value_size: Optional[int] = Field(None, alias='valueSize')


class ValueSetElement(BaseElement):
    value_set: ValueSet

# This corresponds to the floatElementSchema class in the cdElement.ts file
class FloatValues(BaseModel):
    value_type: float = Field('float', alias='valueType')
    cardinality: Cardinality
    value_min_max: Optional[ValueMinMax] = Field(None, alias='valueMinMax')
    values: List[ValueSetValue]
    step_value: Optional[float] = Field(None, alias='stepValue')
    unit: Optional[str]
    value_size: Optional[tuple] = Field(None, alias='valueSize')

class FloatElement(BaseElement):
    float_values: FloatValues



# This corresponds to the integerElementSchema class in the cdElement.ts file
class IntegerValues(BaseModel):
    value_type: int = Field('integer', alias='valueType')
    cardinality: Cardinality
    value_min_max: Optional[ValueMinMax] = Field(None, alias='valueMinMax')
    values: List[ValueSetValue]
    step_value: Optional[int] = Field(None, alias='stepValue')
    unit: Optional[str]
    value_size: Optional[int] = Field(None, alias='valueSize')


class IntegerElement(BaseElement):
    integer_values: IntegerValues


# This corresponds to the booleanElementSchema class in the cdElement.ts file
class BooleanValues(BaseModel):
    value_type: bool = Field('boolean', alias='valueType')
    cardinality: Cardinality
    value_min_max: Optional[ValueMinMax] = Field(None, alias='valueMinMax')
    values: List[ValueSetValue]
    step_value: Optional[bool] = Field(None, alias='stepValue')
    unit: Optional[str]
    value_size: Optional[bool] = Field(None, alias='valueSize')

class BooleanElement(BaseElement):
    boolean_values: BooleanValues


# This corresponds to the elementSchema class in the cdElement.ts file
class Element(BaseModel):
    element: Union[FloatElement, ValueSetElement, IntegerElement, BooleanElement]

class ElementType(str, Enum):
    float = 'float'
    integer = 'integer'
    boolean = 'boolean'
    valueSet = 'valueSet'

class CdElement(BaseModel):
    _data: Element
    _indexCodes: List[IndexCode]

    def __init__(self, baseElementData: Element):
        self._data = baseElementData
        self._indexCodes = [IndexCode(indexCode) for indexCode in (self._data.index_codes or [])]

    @property
    def id(self):
        return self._data.id

    @property
    def parent_id(self):
        return self._data.parent_id

    @property
    def name(self):
        return self._data.name

    @property
    def short_name(self):
        return self._data.short_name

    @property
    def editor(self):
        return self._data.editor

    @property
    def instructions(self):
        return self._data.instructions

    @property
    def synonyms(self):
        return self._data.synonyms

    @property
    def definition(self):
        return self._data.definition

    @property
    def question(self):
        return self._data.question

    @property
    def version(self):
        return self._data.version

    @property
    def index_codes(self):
        return self._indexCodes

    @property
    def authors(self):
        return self._data.authors

    @property
    def history(self):
        return self._data.history

    @property
    def specialty(self):
        return self._data.specialty

    @property
    def references(self):
        return self._data.references

    @property
    def source(self):
        return self._data.source

    @property
    def elementType(self) -> ElementType:
        raise NotImplementedError


class FloatElement(CdElement):
    @property
    def elementType(self) -> ElementType:
        return ElementType.float

    @property
    def float_values(self) -> FloatValues:
        return self._data.element.float_values

    @property
    def min(self):
        return self._data.element.float_values.value_min_max.value_min

    @property
    def max(self):
        return self._data.element.float_values.value_min_max.value_max

    @property
    def stepValue(self):
        return self._data.element.float_values.step_value

    @property
    def unit(self):
        return self._data.element.float_values.unit


class IntegerElement(CdElement):
    @property
    def elementType(self) -> ElementType:
        return ElementType.integer

    @property
    def integer_values(self) -> IntegerValues:
        return self._data.element.integer_values
    @property
    def cardinality(self):
        return self._data.element.integer_values.cardinality

    @property
    def min(self):
        return self._data.element.integer_values.value_min_max.value_min

    @property
    def max(self):
        return self._data.element.integer_values.value_min_max.value_max

    @property
    def stepValue(self):
        return self._data.element.integer_values.step_value

    @property
    def unit(self):
        return self._data.element.integer_values.unit


class BooleanElement(CdElement):
    @property
    def elementType(self) -> ElementType:
        return ElementType.boolean

class ValueSetElement(CdElement):
    @property
    def values(self):
        return self._data.element.value_set.values

    @property
    def elementType(self) -> ElementType:
        return ElementType.valueSet


# This corresponds to the isValueSetElementData function in the cdElement.ts file

class ElementData(BaseModel):
    value_set: Optional[dict] = Field(None, alias='value_set')
    float_values: Optional[dict] = Field(None, alias='float_values')
    integer_values: Optional[dict] = Field(None, alias='integer_values')
    boolean_values: Optional[dict] = Field(None, alias='boolean_values')

class ValueSetElementData(BaseModel):
    value_type: str

class FloatElementData(BaseModel):
    value_type: str

class IntegerElementData(BaseModel):
    value_type: str

class BooleanElementData(BaseModel):
    value_type: str

def is_value_set_element_data(element_data: ElementData) -> bool:
    return element_data.value_set is not None and element_data.value_set.get('value_type') == 'valueSet'

def is_float_element_data(element_data: ElementData) -> bool:
    return element_data.float_values is not None and element_data.float_values.get('value_type') == 'float'

def is_integer_element_data(element_data: ElementData) -> bool:
    return element_data.integer_values is not None and element_data.integer_values.get('value_type') == 'integer'

def is_boolean_element_data(element_data: ElementData) -> bool:
    return element_data.boolean_values is not None and element_data.boolean_values.get('value_type') == 'boolean'


# This corresponds to the CdElementFactory class in the cdElement.ts file
class CdElementFactory:
    @staticmethod
    def create(inData: ElementData) -> CdElement:
        if 'value_set' in inData and inData.value_set.value_type == 'valueSet':
            return ValueSetElement(inData)
        elif 'float_values' in inData and inData.float_values.value_type == 'float':
            return FloatElement(inData)
        elif 'integer_values' in inData and inData.integer_values.value_type == 'integer':
            return IntegerElement(inData)
        elif 'boolean_values' in inData and inData.boolean_values.value_type == 'boolean':
            return BooleanElement(inData)
        else:
            raise ValueError("Unknown element type: doesn't seem to have value_set, float_values, integer_values, or boolean_values.")

## create a CdElement object from JSON data

    @staticmethod
    def createFromJson(json: Union[str, dict]) -> CdElement:
        if isinstance(json, str):
            parsedJson = json.loads(json)
        else:
            parsedJson = json
        inData = ElementData(**parsedJson)
        return CdElementFactory.create(inData)