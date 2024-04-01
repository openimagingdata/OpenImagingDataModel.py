* Date: 4/1/2024

* Goals:


[ ] - `TODO`
1. Transform the RadLex data that is in the ontology database in the `RadLex` collection.
    * Sample RadLex document:

`
{
  "_id": {
    "$oid": "65f84ed1f80fad5323c79c1f"
  },
  "Class ID": "http://radlex.org/RID/RID35591",
  "Preferred Label": "string-of-pearls sign of bowel",
  "Definitions": "Oblique or horizontal row of air bubbles visible on abdominal radiograph; almost always indicates small bowel obstruction; air is trapped between valvulae conniventes along the superior wall of the intestine.",
  "Obsolete": false,
  "Parents": "http://radlex.org/RID/RID29023",
  "http://data": {
    "bioontology": {
      "org/metadata/prefixIRI": "RID35591"
    }
  },
  "http://radlex": {
    "org/RID/Anatomical_Site": "http://radlex.org/RID/RID132",
    "org/RID/Comment": "http://radiology.rsna.org/cgi/content/full/214/1/157",
    "org/RID/Definition": "Oblique or horizontal row of air bubbles visible on abdominal radiograph; almost always indicates small bowel obstruction; air is trapped between valvulae conniventes along the superior wall of the intestine.",
    "org/RID/May_Be_Caused_By": "http://radlex.org/RID/RID4962",
    "org/RID/Preferred_name": "string-of-pearls sign of bowel",
    "org/RID/Preferred_name_German": "string-of-pearls sign of bowel (EN)",
    "org/RID/Related_modality": "http://radlex.org/RID/RID10345",
    "org/RID/Source": "Radiology 2000; 214:157-158"
  }
}
`

* [x] - `Done`
2. Create new branch `ontology_tools` in OIDM.py repo.
    * Create a new directory under `src/openimagingdatamodel/ontology_tools`



* [ ] - `TODO`
3. Work on creating a script that transforms the data from the "inconvenient format" above into a more workable format, consider the following steps:

    * Put it all into a new collection named `radlex`
    * Use the RadLex ID (e.g., `RID3559`) as the ID, not a generated ObjectID
    * All properties in appropriate camel case (e.g., `preferredLabel`)
    * Only have the following top-level properties:
        * `_id`
        * `preferredLabel`
        * `synonyms` - should be a list of strings
        * `parent` - should be just an ID (not a URL)
        * `definition` - a string
    * Pull the properties from the http://radlex property into a separate object, of the form:
        * `anatomicalSite`: `RID132`
        * `comment`: "http://radiology.rsna.org/cgi/content/full/214/1/157"
        * Skip definition if it's already in the top level
        * `mayBeCausedBy`: `RID4962`
        * ...