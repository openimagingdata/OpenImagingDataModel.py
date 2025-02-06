"""Represents a CDE Set with its component Elements."""

from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl
from pydantic.config import ConfigDict
from typing import List, Optional

from .common import (  # noqa: TCH001
    BodyPart,
    Contributors,
    Image,
    IndexCode,
    Modality,
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

    model_config = ConfigDict(
        json_schema_extra={
            "$id": "https://github.com/ACR-RSNA-CDEs/blob/v1.0.0/cde.schema.json",
            "$schema": "http://json-schema.org/draft-07/schema#",
        }
    )
    # "required": ["id", "name", "description", "set_version", "current_status", "elements", "specialties", "schema_version"]
    id: str = Field(..., pattern=r"^(RDES|TO_BE_DETERMINED)\d+", description = "Must be a valid ID", examples = ["RDES42", "RDES1042"])
    name: str = Field(...,  max_length=50, description="Set names should follow conventions listed here: https://rsna.github.io/ACR-RSNA-CDEs/reference/set/", examples = ["CAR/DS Adrenal Nodule"])
    description: str = Field(..., max_length=100, description="Must be 100 or fewer characters long")
    set_version: Version
    schema_version: SchemaVersion
    current_status: Status
    status_history: list[Status] = Field(default_factory=list, description="A history of statuses for the CDE set, with at least one required.")    
    url: Optional[HttpUrl] = Field(default = None, description = "A link to the set on radelement.org" )
    index_codes: list[IndexCode] = Field(default_factory=list)
    body_parts: list[BodyPart] = Field(default_factory=list)
    contributors: Contributors = Field(default = None)   
    specialties: List[Specialty] = Field(default_factory=list)
    modalities: list[Modality] = Field(default_factory = list)
    elements: list[CDEElement] = Field(..., description = "When authoring (e.g., PUT/POST), published elements can be referenced (element_ref_id). GET requests return full element definitions")
    images: list[Image] = Field(default_factory=list)
    references: list[Reference] = Field(default_factory=list)
    
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
    
    
    
 