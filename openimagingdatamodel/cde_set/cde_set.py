"""Represents a CDE Set with its component Elements."""

from pydantic import BaseModel, Field


class Specialty(BaseModel): ...


class Status(BaseModel): ...


class Version(BaseModel): ...


class Organization(BaseModel): ...


class Person(BaseModel): ...


class CDEElement(BaseModel): ...


# https://github.com/RSNA/ACR-RSNA-CDEs/blob/master/cde.schema.json
class CDESet(BaseModel):
    """Represents a CDE Set with its component Elements."""

    id: str = Field(..., regex="^(RDES|TO_BE_DETERMINED)\d+")
    name: str
    description: str
    version: Version
    status: Status
    # url field is a string containing a URL
    url: str = Field(..., regex="^https?://")
