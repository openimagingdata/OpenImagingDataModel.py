# Description: This script is used to batch transform and write the radlex collection to the MongoDB database.
from .radlex_importer import transform_radlex

# function to write batch sizes of 100 back to MongoDB ontologies database 'radlex' collection
def batch_transform_and_write_to_db(collection):
    batch_size = 100
    cursor = collection.find().batch_size(batch_size)
    batch = []
    for doc in cursor:
        transformed_doc = transform_radlex(doc)
        batch.append(transformed_doc.model_dump_json())
        if len(batch) == batch_size:
            collection.insert_many(batch)
            batch = []
    if batch:
        collection.insert_many(batch)




# Example usage to use in the notebook experiment
# batch_transform_and_write_to_db(radlex_collection)
