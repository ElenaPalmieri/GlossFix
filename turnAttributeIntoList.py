from pymongo import MongoClient
from bson.objectid import ObjectId

# annotations contains all the annotations that refer to the tag that was updated
# annotations = db.get_collection('Annotations').find({'type': ObjectId(tag_id)})
# annotations = list(annotations)

# tag_id _id of the tag that changed
# tag_id = '60959cdbd82b27727b373c84'

# correct_annotation_id _id of an annotation made after the tag changed, its attributes will be used as a guide
# correct_annotation_id = '6160135d314baa8534a520f7'

host = 'localhost'
port = 27017

client = MongoClient(host=host, port=port)
db = client.glossProduction


# Fixes the tags that can no longer be edited, but the number of attributes in the tag must be the same
def turn_attribute_into_list(annotations, tag_id, correct_annotation_id):

    for item in annotations:
        if item['_id'] == ObjectId(correct_annotation_id):
            model = item
            annotations.remove(item)

    for item in annotations:
        for i in range(0, len(model['attributes'])):
            if isinstance(model['attributes'][i]['value'], list) and not isinstance(item['attributes'][i]['value'], list):
                previous_attribute = item['attributes'][i]['value']
                item['attributes'][i]['value'] = [previous_attribute]

        db.get_collection('Annotations').update({
                    'task': ObjectId(item['task']),
                    '_id': ObjectId(item['_id']),
                    'type': ObjectId(tag_id)},
                    {'$set': {'attributes': item['attributes']}})





