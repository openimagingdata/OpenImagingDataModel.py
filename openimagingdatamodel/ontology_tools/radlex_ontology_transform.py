"""Utility class for transforming data format in MongoDB ontologies/RadLex database to new format and save to ontologies/radlex collection."""

from pydantic import BaseModel, ConfigDict


# Define the RadLex fields

class RadLexConcept(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

class RadLexProperties(BaseModel):
    anatomicalSite: str | None = None
    comment: str | None = None
    definition: str | None = None
    mayBeCausedBy: str | None = None
    is_A: str | None = None
    source: str | None = None
    relatedModality: str | None = None
    preferredName: str | None = None
    preferredNameGerman: str | None = None


# Define the new document format and fields
class NewDoc(BaseModel):
    id: str
    preferredLabel: str
    synonyms: list[str] | None = None
    parent: str | None = None
    definition: str | None = None
    radlexProperties: RadLexProperties






# function to transform document format
class Transform:
    def __init__(self, doc):
        self.doc = doc

    def transform_func(self) -> dict:
        # Extract RadLex ID from "Class ID" field if it exists
        class_id = self.doc.get("Class ID")
        if class_id:
            radlex_id = class_id.rsplit('/', 1)[-1]
        else:
            # handle cases where "Class ID" field does not exist
            raise ValueError("Class ID field does not exist in the document.")

        synonym_list = self.doc.get("Synonyms")
        if synonym_list:
            synonym_list = synonym_list.replace('|', ', ').split(', ')
        else:
            synonym_list = None

        # create a new object for the properties from the "http://radlex" field
        radlex_properties = self.doc.get('http://radlex', {})
        new_radlex_properties = {}
        for key, value in radlex_properties.items():
            new_key = key.split("/")[-1]
            new_key = ''.join(word.capitalize() for word in new_key.split('_'))
            new_key = new_key[0].lower() + new_key[1:]
            new_value = value.split("/")[-1] if isinstance(value, str) and 'http' in value else value
            new_radlex_properties[new_key] = new_value

        # create a new document with the desired top-level properties
        new_doc = NewDoc(
            id=radlex_id,
            preferredLabel=self.doc.get('Preferred Label', ''),
            synonyms=synonym_list,
            parent=self.doc.get('Parents', '').split('/')[-1] if self.doc.get('Parents') else '',
            definition=self.doc.get('Definitions', ''),
            radlexProperties=RadLexProperties(**new_radlex_properties)
        )

        return new_doc
