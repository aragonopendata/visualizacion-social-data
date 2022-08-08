from elasticsearch import Elasticsearch
from elasticsearch import helpers

import datetime
import json

from os import listdir
from os.path import isfile, join
import glob

class RemoteModel(object):
    def __init__(self):
        self.es = Elasticsearch(
            'http://biv-aodback-01.aragon.local:9200', retry_on_timeout=True)

    def request(self, payload):
        # with open("/tmp/elasticlog.txt", 'w+') as f:
        #     print >>f, "ELASTIC", payload
        return self.es.search(index="escucha", doc_type="data_items", body=payload, request_timeout=30)


    def import_json(self):
        array = glob.glob("./db/*.json")
        for json_file_name in array:
            with open(json_file_name, 'r') as json_file:
                data = json.load(json_file)
                print(json_file_name)
                helpers.bulk(self.es, data)
        print('end')


RemoteModel().import_json()
