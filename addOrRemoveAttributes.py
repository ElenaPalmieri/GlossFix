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


# Adds the new attributes to existing annotations after an update of the type system
def add_new_attribute(annotations, tag_id, correct_annotation_id):
    found_model = False
    model = {}
    for item in annotations:
        print(item['attributes'])
        if item['_id'] == ObjectId(correct_annotation_id):
            model = item
            found_model = True
            annotations.remove(item)

    if found_model:
        for item in annotations:
            for i in range(len(item['attributes']), len(model['attributes'])):
                item['attributes'].append(model['attributes'][i])
            print(item['attributes'])
            db.get_collection('Annotations').update({
                            'task': ObjectId(item['task']),
                            '_id': ObjectId(item['_id']),
                            'type': ObjectId(tag_id)},
                            {'$set': {'attributes': item['attributes']}})
    else:
        print('ERROR: correct annotation not found')


# Removes the deleted attributes form existing annotations
# IMPORTANT: it needs to know the position that the attribute had in the list, so it works for one attribute at a time
def remove_attribute(annotations, tag_id, attribute_position):
    for item in annotations:
        new_attributes = []
        for i in range(0, len(item['attributes'])):
            if i != attribute_position:
                new_attributes.append(item['attributes'][i])
        db.get_collection('Annotations').update({
                        'task': ObjectId(item['task']),
                        '_id': ObjectId(item['_id']),
                        'type': ObjectId(tag_id)},
                        {'$set': {'attributes': new_attributes}})
