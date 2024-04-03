"""Utility class for transforming data format in MongoDB ontologies/RadLex database to new format and save to ontologies/radlex collection."""

from pydantic import BaseModel
from radlex_concept import RadLexConcept

# Define RadLexProperties dictionary to account for "http://radlex" field
RadLexProperties = dict[str, str|list[str]]



# Define the new document format and fields
class NewDoc(BaseModel):
    id: str
    preferred_label: str
    synonyms: list[str] | None = None
    parent: str | None = None
    definition: str | None = None
    radlex_properties: RadLexProperties



# function to transform document format
def transform_radlex(doc: dict) -> RadLexConcept:
    # Extract RadLex ID from "Class ID" field if it exists
    class_id = doc.get("Class ID")
    if class_id:
        radlex_id = class_id.rsplit('/', 1)[-1]
    else:
        # handle cases where "Class ID" field does not exist
        raise ValueError("Class ID field does not exist in the document.")

    synonym_list = doc.get("Synonyms")
    if synonym_list:
        synonym_list = synonym_list.replace('|', ', ').split(', ')
    else:
        synonym_list = None

    # create a new object for the properties from the "http://radlex" field
    radlex_properties = doc.get('http://radlex', {})
    for key, value in radlex_properties.items():
        new_key = key.split("/")[-1]
        new_key = ''.join(word.capitalize() for word in new_key.split('_'))
        new_key = new_key[0].lower() + new_key[1:]
        new_value = value.split("/")[-1] if isinstance(value, str) and 'http' in value else value
        RadLexProperties[new_key] = new_value

    # create a new document with the desired top-level properties
    new_doc = NewDoc(
        id=radlex_id,
        preferred_label=doc.get('Preferred Label', ''),
        synonyms=synonym_list,
        parent=doc.get('Parents', '').split('/')[-1] if doc.get('Parents') else '',
        definition=doc.get('Definitions', ''),
        radlex_properties=RadLexProperties
    )

    return new_doc
