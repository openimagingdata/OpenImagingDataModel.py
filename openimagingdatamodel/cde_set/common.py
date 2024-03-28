from typing import Annotated, Literal

from pydantic import BaseModel, Field, HttpUrl


# Change Specialty to Specialties
class Specialties(BaseModel):
    abbreviation: Literal[
        "AB", "BR", "CA", "CH", "ER", "GI", "GU", "HN", "IR", "MI", "MK", "NR", "OB", "OI", "OT", "PD", "QI", "RS", "VA"
    ]
    name: str


class Version(BaseModel):
    number: int  # TODO: Minimum 1
    date: str  # TODO: Add date format


# Use Annotated to create a type which is a custom string with a specific regex pattern
SchemaVersion = Annotated[
    str,
    Field(
        regex="^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?$"
    ),
]


class Status(BaseModel):
    date: str  # TODO: Add date format
    name: Literal["Proposed", "Published", "Retired"]


class Event(BaseModel):
    date: str  # TODO: Add date format
    status: Status


class Organization(BaseModel):
    name: str
    url: HttpUrl | None = None
    abbreviation: str | None = None
    comment: str | None = None
    role: Literal["author", "sponsor", "translator", "reviewer", "contributor"] | None = None


class Person(BaseModel):
    name: str
    email: str  # TODO: Add email format
    affiliation: str | None = None
    orcid_id: str | None = None
    twitter_handle: str | None = None
    url: HttpUrl | None = None
    role: Literal["Author", "Editor", "Translator", "Reviewer"] | None = None


class Contributors(BaseModel):
    people: list[Person] = Field(default_factory=list)
    organizations: list[Organization] = Field(default_factory=list)


class Reference(BaseModel):
    citation: str = Field(
        description="Required - Provide a bibliographic citation, including all the author names (no et Al)"
    )
    doi_uri: str | None = None  # TODO: Add refex for doi uri
    pubmed_id: str | None = None  # TODO: Add refex for pubmed id
    url: HttpUrl | None = None


class IndexCode(BaseModel):
    system: Literal["RADLEX", "SNOMED", "LOINC", "ACRCOMMON"] | None = None
    code: str | None = None
    display: str | None = None
    url: HttpUrl | None = None


class BodyPart(BaseModel):
    name: str
    index_codes: list[IndexCode] | None = None


class Image(BaseModel):
    url: HttpUrl
    height: int | None = None
    width: int | None = None
    caption: str | None = None
    rights: str | None = None
    contributors: Contributors | None = None
    references: list[Reference] | None = None
