"""Utility class for building up a CDE set."""

import random
from datetime import date
from typing import Any

from caseswitcher import to_snake
from pydantic import BaseModel, ValidationError

from openimagingdatamodel.cde_set import finding_model
from openimagingdatamodel.cde_set.finding_model import FindingModel

from .common import Event, Status, Version
from .element import BooleanElement, FloatElement, FloatValue, IntegerElement, IntegerValue, ValueSet, ValueSetElement
from .set import CDESet


class SetIddict(BaseModel):
    set_id: str
    element_ids: dict[str, str]


class SetFactory:
    @staticmethod
    def random_digits() -> str:
        return "".join(random.choices("0123456789", k=4))

    @staticmethod
    def create_set(name: str, /, description: str | None = None, add_presence_element: bool = False) -> CDESet:
        """Return a default required CDE Set metadata."""

        if not name:
            raise ValueError("Name is required for a CDE Set")

        random_digits = SetFactory.random_digits()
        today = date.today().strftime("%Y-%m-%d")
        version = Version(number=1, date=today)
        status = Status(date=today, name="Proposed")
        history = [Event(date=today, status=status)]
        set = CDESet(
            id=f"TO_BE_DETERMINED{random_digits}",
            name=name,
            description=(description or f"Description for {name}"),
            schema_version="1.0.0",
            set_version=version,
            status=status,
            history=history,
            index_codes=[],
            specialties=[],
        )
        if add_presence_element:
            set.elements.append(SetFactory.create_presence_element(name))
        return set

    @staticmethod
    def default_element_metadata(name) -> dict[str, str | dict[str, Any] | list[Any]]:
        """Return a default required CDE Element metadata."""

        if not name:
            raise ValueError("Name is required for a CDE Element")

        today = date.today().strftime("%Y-%m-%d")
        random_digits = SetFactory.random_digits()

        return {
            "id": f"TO_BE_DETERMINED{random_digits}",
            "name": name,
            "element_version": {
                "number": 1,
                "date": today,
            },
            "schema_version": "1.0.0",
            "status": {
                "date": today,
                "name": "Proposed",
            },
        }

    @staticmethod
    def create_integer_element(
        name: str,
        /,
        min: int | None = None,
        max: int | None = None,
        step: int | None = None,
        unit: str | None = None,
    ) -> IntegerElement:
        """Return an integer element."""
        element_id = "TO_BE_DETERMINED" + SetFactory.random_digits()
        boilerplate = SetFactory.default_element_metadata(name)
        boilerplate["id"] = element_id

        integer_value_args: dict[str, str | int] = {}
        if min is not None:
            integer_value_args["min"] = min
        if max is not None:
            integer_value_args["max"] = max
        if step is not None:
            integer_value_args["step"] = step
        if unit is not None:
            integer_value_args["unit"] = unit
        return IntegerElement(**boilerplate, integer_value=IntegerValue(**integer_value_args))  # type: ignore

    @staticmethod
    def create_float_element(
        name: str,
        /,
        min: float | None = None,
        max: float | None = None,
        step: float | None = None,
        unit: str | None = None,
    ) -> FloatElement:
        """Return a float element."""
        element_id = "TO_BE_DETERMINED" + SetFactory.random_digits()
        boilerplate = SetFactory.default_element_metadata(name)
        boilerplate["id"] = element_id

        float_value_args: dict[str, str | float] = {}
        if min is not None:
            float_value_args["min"] = min
        if max is not None:
            float_value_args["max"] = max
        if step is not None:
            float_value_args["step"] = step
        if unit is not None:
            float_value_args["unit"] = unit
        return FloatElement(**boilerplate, float_value=FloatValue(**float_value_args))  # type: ignore

    @staticmethod
    def create_boolean_element(name: str) -> BooleanElement:
        """Return a boolean element."""
        element_id = "TO_BE_DETERMINED" + SetFactory.random_digits()
        boilerplate = SetFactory.default_element_metadata(name)
        boilerplate["id"] = element_id
        return BooleanElement(**boilerplate, boolean_value="boolean")  # type: ignore

    @staticmethod
    def create_value_set_element(
        name: str,
        values: list[dict[str, str] | str],
        /,
        definition: str | None = None,
        question: str | None = None,
        min_cardinality: int = 1,
        max_cardinality: int = 1,
    ) -> ValueSetElement:
        """Return a value set element."""
        element_id = "TO_BE_DETERMINED" + SetFactory.random_digits()
        boilerplate = SetFactory.default_element_metadata(name)
        boilerplate["id"] = element_id
        if definition:
            boilerplate["definition"] = definition
        if question:
            boilerplate["question"] = question

        assert values and len(values) >= 2, "Value set must have at least two values"

        def check_and_fix_value(value: dict[str, str] | str, ind: int) -> dict[str, str]:
            out_value = value.copy() if isinstance(value, dict) else {"name": value}
            if "name" not in out_value:
                raise ValueError("Value must have a name")
            out_value["code"] = f"{element_id}.{ind}"
            if "description" in out_value:
                out_value["definition"] = out_value["description"]
                del out_value["description"]
            if "value" not in out_value:
                out_value["value"] = to_snake(out_value["name"])
            return out_value

        values = [check_and_fix_value(value, i) for i, value in enumerate(values)]

        value_set = ValueSet.model_validate({
            "min_cardinality": min_cardinality,
            "max_cardinality": max_cardinality,
            "values": values,
        })

        return ValueSetElement(**boilerplate, value_set=value_set)  # type: ignore

    @staticmethod
    def create_presence_element(
        finding_name: str | None = None, /, definition: str | None = None, question: str | None = None
    ) -> ValueSetElement:
        """Return a presence element."""

        name = f"Presence of {finding_name}" if finding_name else "Presence"
        if not definition:
            definition = f"Presence of {finding_name}" if finding_name else "Presence of the feature"
        if not question:
            question = f"Is the {finding_name} present?" if finding_name else "Is the feature present?"

        values: list[dict[str, str] | str] = [
            {
                "value": "absent",
                "name": "Absent",
            },
            {
                "value": "present",
                "name": "Present",
            },
            {
                "value": "unknown",
                "name": "Unknown",
            },
            {
                "value": "indetermiante",
                "name": "Indetermiante",
            },
        ]

        return SetFactory.create_value_set_element(name, values, definition=definition, question=question)

    @staticmethod
    def create_set_from_finding_model(model: FindingModel) -> CDESet:
        try:
            set: CDESet = SetFactory.create_set(model.finding_name)
        except ValidationError as e:
            print(f"Error creating set from model {finding_model}: {e}")
            raise e
        set.description = model.description
        for element in model.attributes:
            new_el: FloatElement | ValueSetElement
            if isinstance(element, finding_model.ChoiceAttribute):
                values: list[dict[str, str] | str] = [value.model_dump() for value in element.values]
                new_el = SetFactory.create_value_set_element(element.name, values)
                for el_value, att_value in zip(new_el.value_set.values, values):
                    if isinstance(att_value, dict) and (description := att_value.get("description")):
                        el_value.definition = description
            if isinstance(element, finding_model.NumericAttribute):
                new_el = SetFactory.create_float_element(
                    element.name, min=element.minimum, max=element.maximum, unit=element.unit
                )
            if element.description:
                new_el.definition = element.description
            set.elements.append(new_el)
        return set

    @staticmethod
    def update_set_ids_from_dict(set: CDESet, dict: SetIddict | dict[str, str | dict[str, str]]) -> None:
        if not isinstance(dict, SetIddict):
            dict = SetIddict.model_validate(dict)
        set.id = dict.set_id
        for element in set.elements:
            element.id = dict.element_ids[element.name]
            if isinstance(element, ValueSetElement):
                for i in range(0, len(element.value_set.values)):
                    element.value_set.values[i].code = f"{element.id}.{i}"
