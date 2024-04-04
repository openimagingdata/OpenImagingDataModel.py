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
    if synonym_list:
        if "|" in synonym_list:
            synonym_list = [synonym_list.strip() for synonym_list in synonym_list.split("|")]
        else:
            synonym_list = [synonym_list]

    # create a new object for the properties from the "http://radlex" field
    original_properties = doc.get("http://radlex", {})
    fixed_properties = {}

    # Query keys to avoid repetition
    query_keys = ['definition', 'synonym', 'synonym_german', 'preferred_name', 'preferred_name_german']

    def get_last_part(input_string: str) -> str:
        return input_string.split("/")[-1] if input_string.startswith("http") else input_string

    for key, value in original_properties.items():
        if not value or key in query_keys:
            continue

        new_key = to_snake(key.split("/")[-1])

        new_value = [get_last_part(item) for item in value.split("|")] if "|" in value else get_last_part(value)

        fixed_properties[new_key] = new_value

    # create a new document with the desired top-level properties
    new_doc = RadLexConcept(
        id=radlex_id,
        preferred_label=doc.get("Preferred Label", ""),
        synonyms=synonym_list,
        parent=doc.get("Parents", "").split("/")[-1] if doc.get("Parents") else "",
        definition=doc.get("Definitions", ""),
        radlex_properties=fixed_properties
    )

    return new_doc
