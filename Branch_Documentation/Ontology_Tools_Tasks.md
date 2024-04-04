* Date: 4/1/2024

* Goals:


[x] - `TODO`
1. Transform ALL RadLex data that is in the ontology database in the `RadLex` collection.
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



* [x] - `TODO`
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

-------------------------------------------------------------------------------------------------------------------------------------------------
Mapping out TODO tasks:
[x] - Create new collection in MongoDB ontology database named `radlex`
[x] - Write a script that at a high-level does this:
        * Takes in each individual RadLex document from MongoDB directory: `ontologies/RadLex`
        * Transforms data into desired format.
        * Pushes transformed data back to MongoDB collection `radlex`
-----------------------------------------------------------------------------------------------------------------------------------------------
Editing Tasks
* Date: 4/3/2024

Part 1: file management
[x] - Rename your file to something like `radlex_importer.py`:
[x] - Move the definition of `RadLexConcept` to a new file, `radlex_concept.py`
[x] - Change `Transform` class to a function named `transform_radlex` that takes an old-style RadLex object as a dict type and returns a `RadLexConcept`



Part 2: In `RadLexConcept`:
[x] - Are you sure we have all the keys that might be used in `RadLexProperties`? There are 75, we only accounted for 9 of them. I checked with a MongoDB query. However, we will NOT use a pydantic class for this as its too much data to detail. Instead we will return a dict of string keys and either string or list of string values.
[x] - Can you make sure we're using appropriate **snake case** for all the property names in `RadLexProperties`? (e.g., is_a, may_be_caused_by, etc.)
[x] - Be aware that in fact, the values of `RadLexProperties` might be **lists of strings** rather than **simple strings**, I think
[x] - Don't include `preferredName` in the properties object, because we already have it at the top
[x] - When we make the real `RadLexConcept` class for working with the cleaned up data, let's convert the keys from camel to snake case using a `field validator`.

Part 3: move away from trying to create a specific `RadLexProperties` type the way you do. There are so many possible tags there, we don't want to try to represent them all in an object.
[x] - Instead, let's just put them all in a `radlex_properties` dictionary, which we can type as `dict[str, str|list[str]]`.
[x]The only processing we should do is:
    * Convert the property names to camel case when we write to the database
    * See if there are pipe characters in the value; if there are, split into separate strings in a list. (That's the str | list[str] above.)
[x] - Don't do the case conversions yourself--import a useful library, https://pypi.org/project/case-switcher/

---------------------------------------------------------------------------------------------------------------------------------------------------------------------
More Code Change Tasks
Date: 4/3/2024

[x] - `transform_radlex()` function => needs to include code to look in properties dict to see if multiple '|' separated values, if so, split and turn into list.
      * This step needs to occur before transforming the `http://.....RID23434` into `RID23434`
[x] - Do NOT include **synonyms** or **preferred terms** in `radlex_properties` (these are already in the top-level)



camelCase conversion back to MongoDB database
[x] - make sure we have camelCase for property names for BOTH `top-level` and `sub-object` in the database.
[x] - Write some code that goes through the RadLex collection 100 elements at a time, transforms them, and batch-writes them back to the radlex collection.
    * Purpose: Use `radlex_concept.py` file and the `RadLexConcept` objects created/formatted to then port these back to the MongoDB instance.
[x] - Demo the JSON dump of what you're proposing to write back to the database.

[x] - May want to use a `field_serializer` for JSON exports. link: https://docs.pydantic.dev/latest/api/functional_serializers/#pydantic.functional_serializers.field_serializer
    * using the field_serializer from Pydantic for enabling custom field serialization.
    * Used to serialize the data as a sorted list.
    * Goal:
      * our internal representation is snake_case
      * just apply to radlex properties field.
      * use `field_serializer decorator` => takes a function and wraps it with other functionality => gets called whenever you call either the `model_dump` or `model_dump_json` methods
      * when call decorator it gives parameters for how you want it to do the wrapping.
      * `radlex_properties` is the field we want to apply it to.
      * use default 'always' for the when_used parameters
      * Take in an argument called "in_props" => str | list[str] => dict[str => str | list[str]]
      * function to use:
            `@field_serializer(radlex_properties)`
            `def change_keys_to_camel_case(in_props: dict[str, str|list[str]) → dict[str, str|list[str]):`
                  `out = { camel_case(k): v for k, v in in_props.items } return out`
      * use Pydantic alias generator class => convert all snake_case to camelCase (Uses a built-in AliasGenerator camelCase generator)



[x] - Once JSON dump is approved, write code to port back to MongoDB `radlex` collection in the `ontology` database.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
More Code Change Tasks
Date: 4/4/2024

[] - Fix the JSON output for `radlexProperties` so that:
  * The HTML links are output as a **list of strings**, for example for `hasRegionalPart` becomes: ['RID39870',RID41870','RID39765']

`{
  "_id": "RID49379",
  "preferredLabel": "left tibia",
  "parent": "RID2885",
  "definition": "",
  "radlexProperties": {
    "fmaid": "24478",
    "hasConstitutionalPart": "RID49038",
    "hasRegionalPart": [
      "http://radlex.org/RID/RID39870",
      "http://radlex.org/RID/RID41870",
      "http://radlex.org/RID/RID39765"
    ]
  }`

------------------------------------------------------------------------------------------------------------------------------------------------
Future Notes:
* The next step is that we generate wrapper libraries for the concepts in the database: RadLexConcept and SnomedConcept
* We can also create RadLexConceptRepo and SnomedConceptRepo for getting the data from the database and populating such objects.
