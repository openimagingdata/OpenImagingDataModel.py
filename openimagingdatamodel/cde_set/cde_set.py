"""Represents a CDE Set with its component Elements."""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Union, Array
import requests

# The order of classes below is based off the order of imports from the cdeSet.ts file
class Specialty(BaseModel): ...

class Version(BaseModel): ...

class Event(BaseModel): ...

class Organization(BaseModel): ...

class Person(BaseModel): ...

class Authors(BaseModel): ...

class Reference(BaseModel): ...

class BodyPart(BaseModel): ...

class CDEElement(BaseModel): ...

class IndexCode(BaseModel): ...

class Status(BaseModel): ...


# https://github.com/RSNA/ACR-RSNA-CDEs/blob/master/cde.schema.json
class CDESet(BaseModel):
    """Represents a CDE Set with its component Elements."""

    id: str = Field(..., regex="^(RDES|TO_BE_DETERMINED)\d+", description='Must be a valid ID')
    name: str = Field(..., max_length=50, description='Must be 50 or fewer characters long')
    description: str = Field(..., max_length=100, description='Must be 100 or fewer characters long')
    version: Version
    status: Status
    # url field is a string containing a URL
    url: HttpUrl # str = Field(..., regex="^https?://") - can do it this way or use pydantic built-in HttpUrl class that does the same thing
    index_codes: Array[IndexCode]
    body_parts: Array[BodyPart]
    authors: List[Union[Person, Organization]]
    history: Array[Event]
    specialty: Array[Specialty]
    elements: Array[CDEElement]
    references: Array[Reference]

#question about code above, the RSNA data type or most of these is an 'array': it can be coded as: index_codes: List[IndexCode] and still return an array in pydantic.
# however, you can also import Array from typing and use it as shown above.
# you can also use a pydantic library called 'pydantic-numpy' and use it to convert the array to a numpy array. But I am guessing we don't want to do that because
# it would convert the array to the default numpy data type which is float. Correct?
    # I assume we want to keep the data type as an array of strings, so we can use the array data type from the typing library or the list method? -Adam


class CDESetProcessor:
    def __init__(self, data: CDESet):
        self.data = data
        self.index_codes = [IndexCode(**code) for code in data.index_codes]
        self.body_parts = [BodyPart(**part) for part in data.body_parts]
        self.authors = [Person(**author) if 'person' in author else Organization(**author) for author in data.authors]
        self.elements = [CDEElement(**element) for element in data.elements]


    @staticmethod
    def fetch_from_repo(rdes_id: str) -> Optional['CDESetProcessor']:
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