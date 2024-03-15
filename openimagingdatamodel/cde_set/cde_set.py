"""Represents a CDE Set with its component Elements."""

from __future__ import annotations

from enum import StrEnum

import requests
from pydantic import BaseModel, Field, HttpUrl


# The order of classes below is based off the order of imports from the cdeSet.ts file
class Specialty(BaseModel): ...


class Version(BaseModel): ...


class Event(BaseModel): ...


class Organization(BaseModel): ...


class Person(BaseModel): ...


class Authors(BaseModel): ...


class Reference(BaseModel): ...


class CDEElement(BaseModel): ...


# These classes correspond to the indexCode.ts file in OIDM
class SystemEnum(StrEnum):
    RADLEX = "RADLEX"
    SNOMEDCT = "SNOMEDCT"
    LOINC = "LOINC"


class IndexCode(BaseModel):
    system: SystemEnum
    code: str
    display: str | None = None
    href: HttpUrl | None = None


class BodyPart(BaseModel):
    name: str
    index_codes: list[IndexCode] = Field(default_factory=list)


class Status(BaseModel): ...


# https://github.com/RSNA/ACR-RSNA-CDEs/blob/master/cde.schema.json
class CDESet(BaseModel):
    """Represents a CDE Set with its component Elements."""

    id: str = Field(..., pattern="^(RDES|TO_BE_DETERMINED)\d+", description="Must be a valid ID")
    name: str = Field(..., max_length=50, description="Must be 50 or fewer characters long")
    description: str = Field(..., max_length=100, description="Must be 100 or fewer characters long")
    version: Version
    status: Status
    url: HttpUrl
    index_codes: list[IndexCode] = Field(default_factory=list)
    body_parts: list[BodyPart] = Field(default_factory=list)
    authors: list[Person | Organization] = Field(default_factory=list)
    history: list[Event] = Field(default_factory=list)
    specialty: list[Specialty] = Field(default_factory=list)
    elements: list[CDEElement] = Field(default_factory=list)
    references: list[Reference] = Field(default_factory=list)


class CDESetProcessor:
    def __init__(self, data: CDESet):
        self.data = data
        self.index_codes = [IndexCode(**code) for code in data.index_codes]
        self.body_parts = [BodyPart(**part) for part in data.body_parts]
        self.authors = [Person(**author) if "person" in author else Organization(**author) for author in data.authors]
        self.elements = [CDEElement(**element) for element in data.elements]

    @staticmethod
    def fetch_from_repo(rdes_id: str) -> CDESetProcessor | None:
        rad_element_api = f"https://api3.rsna.org/radelement/v1/sets/{rdes_id}"
        response = requests.get(rad_element_api)
        if response.status_code != 200:
            print(f"HTTP error: {response.status_code}")
            return None
        json_data = response.json()
        cde_set_data = CDESet.model_validate_json(json_data)
        return CDESetProcessor(cde_set_data)

    @property
    def id(self):
        return self.data.id

    @property
    def name(self):
        return self.data.name

    @property
    def description(self):
        return self.data.description

    @property
    def version(self):
        return self.data.version

    @property
    def index_codes(self):
        return self.data.index_codes

    @property
    def url(self):
        return self.data.url

    @property
    def body_parts(self):
        return self.data.body_parts

    @property
    def authors(self):
        return self.data.authors

    @property
    def history(self):
        return self.data.history

    @property
    def specialty(self):
        return self.data.specialty

    @property
    def references(self):
        return self.data.references

    @property
    def elements(self):
        return self.data.elements
