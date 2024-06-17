import pytest
from openimagingdatamodel import CDESet
from openimagingdatamodel.cde_set.element import (
    BooleanElement,
    FloatElement,
    IntegerElement,
    ValueSetElement,
)
from openimagingdatamodel.cde_set.set_factory import SetFactory
from openimagingdatamodel.observation.observation import (
    BooleanComponent,
    CodeableConcept,
    CodeableConceptComponent,
    Identifier,
    Observation,
)
from openimagingdatamodel.observation.observation_factory import (
    ComponentValueMap,
    ObservationFactory,
)


@pytest.fixture
def boolean_element() -> BooleanElement:
    el = SetFactory.create_boolean_element("has feature")
    return el


@pytest.fixture
def float_element() -> FloatElement:
    el = SetFactory.create_float_element("density", min=-1000, max=1000, unit="HU")
    return el


@pytest.fixture
def integer_element() -> IntegerElement:
    el = SetFactory.create_integer_element("count", min=-0)
    return el


@pytest.fixture
def value_set_element() -> ValueSetElement:
    values: list[dict[str, str] | str] = ["mild", "moderate", "severe", "indeterminate"]
    el = SetFactory.create_value_set_element("severity", values)
    return el


@pytest.fixture
def cde_set(boolean_element, float_element, integer_element, value_set_element) -> CDESet:
    set = SetFactory.create_set("example finding", add_presence_element=True)
    set.elements.extend([boolean_element, float_element, integer_element, value_set_element])
    return set


class TestObservationFactory:
    def test_generate_observation_id(self, cde_set: CDESet):
        observation_id = ObservationFactory.generate_observation_id(cde_set)
        assert isinstance(observation_id, str)
        assert len(observation_id) > 0

    def test_generate_observation_identifier(self):
        identifier = ObservationFactory.generate_observation_identifier()
        assert isinstance(identifier, Identifier)
        assert len(identifier.value) > 0

    def test_create_cde_set_code(self, cde_set: CDESet):
        code = ObservationFactory.create_cde_set_code(cde_set)
        assert isinstance(code, CodeableConcept)
        assert len(code.codings) > 0
        assert code.codings[0].code == cde_set.id

    def test_element_to_code(self, boolean_element: BooleanElement):
        code = ObservationFactory.element_to_code(boolean_element)
        assert isinstance(code, CodeableConcept)
        assert len(code.codings) > 0
        assert code.codings[0].code == boolean_element.id

    def test_wrap_value_set_value(self, value_set_element: ValueSetElement):
        value = "mild"
        codeable_concept = ObservationFactory.wrap_value_set_value(value_set_element, value)
        assert isinstance(codeable_concept, CodeableConcept)
        assert len(codeable_concept.codings) > 0
        assert codeable_concept.codings[0].code.startswith(value_set_element.id)

    def test_create_boolean_component(self, boolean_element):
        value = True
        component = ObservationFactory.create_component(boolean_element, value)
        assert isinstance(component, BooleanComponent)
        assert component.code.codings[0].code == boolean_element.id

    def test_create_value_set_component(self, value_set_element):
        value = "mild"
        component = ObservationFactory.create_component(value_set_element, value)
        assert isinstance(component, CodeableConceptComponent)
        assert component.value_codeable_concept.codings[0].code.startswith(value_set_element.id)

    def test_create_observation(self, cde_set):
        observation = ObservationFactory.create_observation(cde_set)
        assert isinstance(observation, Observation)
        assert observation.id_
        assert observation.status

    def test_create_observation_with_component_values(self, cde_set) -> None:
        component_values: ComponentValueMap = {
            "has feature": False,
            "density": 123.3,
            "count": 3,
            "severity": "mild",
        }
        observation = ObservationFactory.create_observation(cde_set, component_values=component_values)
        assert isinstance(observation, Observation)
        assert observation.id_
        assert observation.status
        assert len(observation.components) == len(component_values)
