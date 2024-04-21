import uuid
from typing import Any, Final, Mapping, TypeAlias

from caseswitcher import to_snake
from nanoid import generate as generate_nanoid

from openimagingdatamodel import CDESet
from openimagingdatamodel.cde_set.element import (
    BooleanElement,
    CDEElement,  # noqa: TCH001
    FloatElement,
    IntegerElement,
    ValueSetElement,
    ValueSetValue,
)

from .observation import (
    BooleanComponent,
    Code,
    CodeableConcept,
    CodeableConceptComponent,
    Component,
    Identifier,
    IntegerComponent,
    Observation,
    Reference,
    StatusValue,
    StringComponent,
)

ComponentValue: TypeAlias = str | int | float | bool
ComponentValueMap: TypeAlias = Mapping[str, ComponentValue]


class ObservationFactory:
    @classmethod
    def generate_observation_id(cls) -> str:
        """Create a unique observation ID."""
        finding_name = to_snake(cls.cde_set.name)
        return f"{finding_name}_{generate_nanoid(size=10)}"

    DEFAULT_IDENTIFIER_SYSTEM: Final[str] = "urn:dicom:uid"

    @classmethod
    def generate_observation_identifier(
        cls, identifier: str | None = None, system: str = DEFAULT_IDENTIFIER_SYSTEM
    ) -> Identifier:
        """Create a unique observation identifier.

        Typically, for an imaging observation, we will use the DICOM UID system.
        http://dicom.nema.org/dicom/2013/output/chtml/part05/chapter_B.html

        Specifically, we use:
        B.2 UUID Derived UID:
        UID may be constructed from the root "2.25." followed by a decimal representation of
        a Universally Unique Identifier (UUID). That decimal representation treats the 128 bit
        UUID as an integer, and may thus be up to 39 digits long (leading zeros must be suppressed).
        """

        identifier = identifier or "urn:oid:2.25." + str(uuid.uuid4().int)
        return Identifier.model_parse(system=system, value=identifier)

    RADELEMENT_URL: Final[str] = "https://www.radelement.org"

    @classmethod
    def create_cde_set_code(cls, cde_set: CDESet) -> Code:
        """Use a CDESet to create a Code for the `code` element of an Observation."""
        return Code.model_parse(
            codings=[
                {
                    "system": cls.RADELEMENT_URL,
                    "code": cde_set.id,
                    "display": cde_set.name,
                }
            ]
        )

    @classmethod
    def element_to_code(cls, element) -> CodeableConcept:
        return CodeableConcept.model_parse(
            codings=[
                {
                    "system": cls.RADELEMENT_URL,
                    "code": element.id,
                    "display": element.name,
                }
            ]
        )

    @classmethod
    def wrap_value_set_value(cls, element: ValueSetElement, value: str) -> CodeableConceptComponent:
        """Wrap a ValueSetElement value in a CodeableConceptComponent."""
        el_value: ValueSetValue = element.get_value(value)
        element_code = cls.element_to_code(element)
        return CodeableConceptComponent.model_parse(
            code=element_code,
            value_codeable_concept=CodeableConcept.model_parse(
                codings=[
                    {
                        "system": cls.RADELEMENT_URL,
                        "code": el_value.code,
                        "display": el_value.name,
                    }
                ]
            ),
        )

    @classmethod
    def create_component(cls, element: CDEElement, value: ComponentValue) -> Component:
        """Create an appropriate Component object from a CDEElement and a value."""
        code = cls.element_to_code(element)
        if isinstance(element, ValueSetElement):
            if not isinstance(value, str):
                raise ValueError(f"Value must be a string for ValueSetElement {element.id}")
            value_codeable_concept: CodeableConcept = cls.wrap_value_set_value(element, value)
            return CodeableConceptComponent.model_parse(code=code, value_codeable_concept=value_codeable_concept)
        if isinstance(element, BooleanElement):
            if not isinstance(value, (bool, float, int)):
                raise ValueError(f"Value must be a boolean or number for BooleanElement {element.id}")
            return BooleanComponent.model_parse(code=code, value_boolean=bool(value))
        if isinstance(element, FloatElement):
            value = float(value)
            if not isinstance(value, float):
                raise ValueError(f"Value must be a number for FloatElement {element.id}")
            return StringComponent.model_parse(code=code, value_string=str(value))
        if isinstance(element, IntegerElement):
            value = int(value)
            if not isinstance(value, int):
                raise ValueError(f"Value must be an integer for IntegerElement {element.id}")
            return IntegerComponent.model_parse(code=code, value_integer=value)

    DEFAULT_STATUS: Final[StatusValue] = "preliminary"

    @classmethod
    def create_observation(
        cls,
        cde_set: CDESet,
        /,
        id: str | None = None,
        identifier: str | Identifier | None = None,
        status: StatusValue = DEFAULT_STATUS,
        subject: Reference | None = None,
        focus: list[Mapping[str, Any]] | None = None,
        derived_from: list[Reference] | None = None,
        body_site: CodeableConcept | None = None,
        component_values: ComponentValueMap | None = None,
    ) -> Observation:
        """Create an Observation object from a CDESet and other parameters.

        Args:
            cde_set: The CDESet object to use for the code element.
            id: The ID of the observation (auto-generated if not provided).
            identifier: The identifier of the observation (auto-generated if not provided).
            status: The status of the observation (defaults to "preliminary").
            subject: The subject of the observation.
            focus: The focus of the observation.
            derived_from: The derived_from of the observation.
            body_site: The body_site of the observation.
            component_values: A mapping of CDE names or IDs to values.
        """
        id = id or cls.generate_observation_id()
        if not isinstance(identifier, Identifier):
            identifier = cls.generate_observation_identifier(identifier)
        code: Code = cls.create_cde_set_code(cde_set)
        other_kwargs = {}
        if subject:
            other_kwargs["subject"] = subject
        if focus:
            other_kwargs["focus"] = focus
        if derived_from:
            other_kwargs["derived_from"] = derived_from
        if body_site:
            other_kwargs["body_site"] = body_site
        if component_values:
            components = [
                cls.create_component(cde_set.get_element(el_name), value) for el_name, value in component_values.items()
            ]
            other_kwargs["components"] = components
        return Observation(id=id, identifiers=[identifier], code=code, status=status, **other_kwargs)
