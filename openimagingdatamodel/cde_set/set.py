"""Represents a CDE Set with its component Elements."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, HttpUrl

if TYPE_CHECKING:
    from .common import BodyPart, Contributors, Event, IndexCode, Reference, SchemaVersion, Specialty, Status, Version
    from .element import CDEElement


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
