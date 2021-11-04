from pymongo import MongoClient
from bson.objectid import ObjectId


# annotations is a list of all the annotation on that document
# annotations = db.get_collection('Annotations').find({'document': ObjectId(document_id)})
# annotations = list(annotations)
# document_id is the _id of the document that was updated
# document_id = '613b35bd54a6c72a95df633a'

# start is the number that identifies the position where the text was inserted
# start = 643

# length is the length of the inserted text
# length = 6

host = 'localhost'
port = 27017

client = MongoClient(host=host, port=port)
db = client.glossProduction


def shift_tags(annotations, start, length):
    
    for item in annotations:
        if item['start'] >= start:
            item['start'] = item['start'] + length
            item['end'] = item['end'] + length
            db.get_collection('Annotations').update({
                'task': ObjectId(item['task']),
                '_id': ObjectId(item['_id']),
                'type': ObjectId(item['type'])},
                {'$set': {'start': item['start'], 'end': item['end']}})
