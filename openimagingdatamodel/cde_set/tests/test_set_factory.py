import re
from typing import Any, Final

import pytest
from openimagingdatamodel.cde_set.element import BooleanElement, FloatElement, IntegerElement, ValueSetElement
from openimagingdatamodel.cde_set.finding_model import FindingModel
from openimagingdatamodel.cde_set.set import CDESet
from openimagingdatamodel.cde_set.set_factory import SetFactory

PYTEST_VERSION = pytest.__version__

SET_ELEMENT_ID_REGEX = r"TO_BE_DETERMINED\d{4}"


def test_random_digits():
    digits = SetFactory.random_digits()
    assert isinstance(digits, str)
    assert digits.isdigit()


def test_create_set():
    name = "Test Set"
    cde_set = SetFactory.create_set(name)
    assert isinstance(cde_set, CDESet)
    assert cde_set.name == name
    assert re.match(SET_ELEMENT_ID_REGEX, cde_set.id)
    assert len(cde_set.elements) == 0


def test_default_element_metadata():
    name = "Test Element"
    metadata = SetFactory.default_element_metadata(name)
    assert isinstance(metadata, dict)
    assert metadata["name"] == name


def test_create_integer_element():
    name = "Test Integer Element"
    element = SetFactory.create_integer_element(name, min=0, max=10, step=1, unit="cm")
    assert isinstance(element, IntegerElement)
    assert element.name == name
    assert element.integer_value.min == 0
    assert element.integer_value.max == 10
    assert element.integer_value.step == 1
    assert element.integer_value.unit == "cm"


def test_create_float_element():
    name = "Test Float Element"
    element = SetFactory.create_float_element(name, min=0.0, max=1.0, step=0.1, unit="m")
    assert isinstance(element, FloatElement)
    assert element.name == name
    assert element.float_value.min == 0.0
    assert element.float_value.max == 1.0
    assert element.float_value.step == 0.1
    assert element.float_value.unit == "m"


def test_create_boolean_element():
    name = "Test Boolean Element"
    element = SetFactory.create_boolean_element(name)
    assert isinstance(element, BooleanElement)
    assert element.name == name
    assert element.boolean_value == "boolean"


def test_create_value_set_element():
    name = "Test Value Set Element"
    values = ["Value 1", "Value 2", "Value 3"]
    element = SetFactory.create_value_set_element(name, values, definition="Definition", question="Question")
    assert isinstance(element, ValueSetElement)
    # Assert that the element ID has the expected format
    assert re.match(SET_ELEMENT_ID_REGEX, element.id)
    assert element.name == name
    assert element.definition == "Definition"
    assert element.question == "Question"
    assert element.value_set.min_cardinality == 1
    assert element.value_set.max_cardinality == 1
    assert len(element.value_set.values) == 3
    first_value = element.value_set.values[0]
    assert first_value.name == "Value 1"
    # Assert that the value code is in the expected format
    assert first_value.code == f"{element.id}.0"


def test_create_presence_element():
    finding_name = "Test Finding"
    element = SetFactory.create_presence_element(finding_name)
    assert isinstance(element, ValueSetElement)
    assert re.match(SET_ELEMENT_ID_REGEX, element.id)
    assert element.name == finding_name
    assert element.definition == f"Presence of {finding_name}"
    assert element.value_set.min_cardinality == 1
    assert element.value_set.max_cardinality == 1
    assert len(element.value_set.values) == 4
    first_value = element.value_set.values[0]
    assert first_value.name == "Absent"
    assert first_value.code == f"{element.id}.0"


def test_create_set_with_presence_element():
    finding_name = "Test Finding"
    description = "Description of the test finding"
    cde_set = SetFactory.create_set(finding_name, description=description, add_presence_element=True)
    assert isinstance(cde_set, CDESet)
    assert cde_set.name == finding_name
    assert re.match(SET_ELEMENT_ID_REGEX, cde_set.id)
    assert cde_set.description == description
    assert len(cde_set.elements) == 1
    presence_element = cde_set.elements[0]
    assert presence_element.name == f"Presence of {finding_name}"
    assert re.match(SET_ELEMENT_ID_REGEX, presence_element.id)
    assert presence_element.value_set.min_cardinality == 1
    assert len(presence_element.value_set.values) == 4
    first_value = presence_element.value_set.values[0]
    assert first_value.name == "Absent"
    assert first_value.code == f"{presence_element.id}.0"


# Create a fixture loading a JSON file with a finding model

FINDING_MODEL_DATA: Final[dict[str, str | list[Any]]] = {
    "finding_name": "Test Finding",
    "description": "Description of the test finding",
    "attributes": [
        {
            "name": "Size",
            "type": "numeric",
            "minimum": 0,
            "maximum": 10,
            "unit": "cm",
        },
        {
            "name": "Shape",
            "type": "choice",
            "values": [
                {"name": "Round", "description": "The shape is round"},
                {"name": "Oval", "description": "The shape is oval"},
                {"name": "Irregular", "description": "The shape is irregular"},
            ],
        },
        {
            "name": "Presence",
            "type": "choice",
            "values": [
                {"name": "Absent", "description": "The feature is not present"},
                {"name": "Present", "description": "The feature is present"},
                {"name": "Unknown", "description": "It is unknown whether the feature is present"},
                {"name": "Indeterminate", "description": "It is indeterminate whether the feature is present"},
            ],
        },
    ],
}


@pytest.fixture
def finding_model() -> FindingModel:
    return FindingModel.model_validate(FINDING_MODEL_DATA)


def test_create_set_from_finding_model(finding_model):
    cde_set = SetFactory.create_set_from_finding_model(finding_model)
    assert isinstance(cde_set, CDESet)
    assert cde_set.name == finding_model.finding_name
    assert re.match(SET_ELEMENT_ID_REGEX, cde_set.id)
    assert cde_set.description == finding_model.description
    assert len(cde_set.elements) == 3
    size_element = cde_set.elements[0]
    assert size_element.name == "Size"
    assert isinstance(size_element, FloatElement)
    assert size_element.float_value.min == 0
    assert size_element.float_value.max == 10
    assert size_element.float_value.unit == "cm"
    shape_element = cde_set.elements[1]
    assert shape_element.name == "Shape"
    assert isinstance(shape_element, ValueSetElement)
    assert shape_element.value_set.min_cardinality == 1
    assert len(shape_element.value_set.values) == 3
    presence_element = cde_set.elements[2]
    assert presence_element.name == "Presence"
    assert isinstance(presence_element, ValueSetElement)
    assert presence_element.value_set.min_cardinality == 1
    assert len(presence_element.value_set.values) == 4
    first_value = presence_element.value_set.values[0]
    assert first_value.code == f"{presence_element.id}.0"
    assert first_value.name == "Absent"
    assert first_value.definition == "The feature is not present"
