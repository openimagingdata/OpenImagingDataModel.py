"""Utility class for building up a CDE set."""

import random
from datetime import date

from openimagingdatamodel.cde_set.element import ValueSetElement
from openimagingdatamodel.cde_set.set import CDESet


class SetFactory:
    @staticmethod
    def random_digits() -> str:
        return "".join(random.choices("0123456789", k=4))

    @staticmethod
    def default_set_metadata(name: str) -> CDESet:
        """Return a default required CDE Set metadata."""

        assert name, "Name is required for a CDE Set"
        random_digits = SetFactory.random_digits()
        today = date.today().strftime("%Y-%m-%d")
        CDESet(
            id=f"TO_BE_DETERMINED{random_digits}",
            name=name,
            description=f"Description for {name}",
            schema_version="1.0.0",
            set_version={
                "number": 1,
                "date": today,
            },
            status={
                "date": today,
                "name": "Proposed",
            },
            history=[
                {
                    "date": today,
                    "status": "Proposed",
                }
            ],
            index_codes=[],
            specialties=[],
        )

    @staticmethod
    def default_element_metadata(name) -> dict[str, str | dict | list]:
        """Return a default required CDE Element metadata."""
        assert name, "Name is required for a CDE Element"
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
    def presence_element() -> ValueSetElement:
        """Return a presence element."""
        element_id = "TO_BE_DETERMINED" + SetFactory.random_digits()
        boilerplate = SetFactory.default_element_metadata("Presence")
        boilerplate["id"] = element_id
        boilerplate["definition"] = "Presence of the feature"
        boilerplate["question"] = "Is the feature present?"

        return ValueSetElement(
            **boilerplate,
            value_set={
                "min_cardinality": 0,
                "max_cardinality": 1,
                "values": [
                    {
                        "code": f"{element_id}.0",
                        "value": "absent",
                        "name": "Absent",
                    },
                    {
                        "code": f"{element_id}.1",
                        "value": "present",
                        "name": "Present",
                    },
                    {
                        "code": f"{element_id}.2",
                        "value": "unknown",
                        "name": "Unknown",
                    },
                    {
                        "code": f"{element_id}.3",
                        "value": "indetermiante",
                        "name": "indetermiante",
                    },
                ],
            },
        )
