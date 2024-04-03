"""Utility class for transforming data format in MongoDB ontologies/RadLex database to new format and
save to ontologies/radlex collection."""

from caseswitcher import to_snake

from .radlex_concept import RadLexConcept


# function to transform document format
def transform_radlex(doc: dict) -> RadLexConcept:
    # Extract RadLex ID from "Class ID" field if it exists
    class_id = doc.get("Class ID")
    if class_id:
        radlex_id = class_id.rsplit("/", 1)[-1]
    else:
        # handle cases where "Class ID" field does not exist
        raise ValueError("Class ID field does not exist in the document.")

    synonym_list = doc.get("Synonyms")
    synonym_list = synonym_list.replace("|", ", ").split(", ") if synonym_list else None

    # create a new object for the properties from the "http://radlex" field
    original_properties = doc.get("http://radlex", {})
    fixed_properties = {}
    for key, value in original_properties.items():
        new_key = key.split("/")[-1]
        new_key = to_snake(new_key)
        new_value = value.split("/")[-1] if isinstance(value, str) and "http" in value else value
        fixed_properties[new_key] = new_value

    # create a new document with the desired top-level properties
    new_doc = RadLexConcept(
        id=radlex_id,
        preferred_label=doc.get("Preferred Label", ""),
        synonyms=synonym_list,
        parent=doc.get("Parents", "").split("/")[-1] if doc.get("Parents") else "",
        definition=doc.get("Definitions", ""),
        radlex_properties=fixed_properties,
    )

    return new_doc
