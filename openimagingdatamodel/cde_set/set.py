"""Represents a CDE Set with its component Elements."""

from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl

from .common import (  # noqa: TCH001
    BodyPart,
    Contributors,
    Event,
    IndexCode,
    Reference,
    SchemaVersion,
    Specialty,
    Status,
    Version,
)
from .element import CDEElement  # noqa: TCH001


# https://github.com/RSNA/ACR-RSNA-CDEs/blob/master/cde.schema.json
class CDESet(BaseModel):
    """Represents a CDE Set with its component Elements."""

    id: str = Field(..., pattern="^(RDES|TO_BE_DETERMINED)\d+", description="Must be a valid ID")
    name: str = Field(..., max_length=50, description="Must be 50 or fewer characters long")
    description: str = Field(..., max_length=100, description="Must be 100 or fewer characters long")
    set_version: Version
    schema_version: SchemaVersion
    status: Status
    url: HttpUrl | None = None
    index_codes: list[IndexCode] = Field(default_factory=list)
    body_parts: list[BodyPart] | None = None
    contributors: Contributors | None = None
    history: list[Event] = Field(default_factory=list)
    specialties: list[Specialty] = Field(default_factory=list)
    elements: list[CDEElement] = Field(default_factory=list)  # TODO: Require at least one element
    references: list[Reference] | None = None

    def get_element(self, element: str) -> CDEElement:
        """Get a component CDEElement by name or ID."""
        element = element.casefold()
        if not hasattr(self, "_element_index"):
            self._element_index = {}
            for el in self.elements:
                self._element_index[el.id.casefold()] = el
                self._element_index[el.name.casefold()] = el
        if element in self._element_index:
            return self._element_index[element]
        raise ValueError(f"Element '{element}' not found in CDE Set '{self.id}' ({self.name})")
