from elasticsearch import Elasticsearch
from elasticsearch import helpers

import datetime
import json


class RemoteModel(object):
    def __init__(self):
        self.es = Elasticsearch(
            'http://biv-aodback-01.aragon.local:9200', retry_on_timeout=True)

    def request(self, payload):
        # with open("/tmp/elasticlog.txt", 'w+') as f:
        #     print >>f, "ELASTIC", payload
        return self.es.search(index="escucha", doc_type="data_items", body=payload, request_timeout=1000)


    def last(self, query='*', region='*', min_published_on=None, max_published_on=None, size=1):
        payload = {
            "size": 1,
            "sort": {
                "published_on": {
                    "order": "desc"
                }
            },
        }
        print(self.request(payload)['hits']['hits'][0]['_source']['published_on'])
        # return 




RemoteModel().last()
