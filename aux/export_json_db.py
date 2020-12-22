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
        return self.es.search(index="escucha", doc_type="data_items", body=payload, request_timeout=30)

    def get_escucha(self, size=1, gte=1385855999999, polarity=None):
        payload = {
            "sort": {"published_on": "asc"},
            "size": size,
            "query": {
                "bool": {
                    # "must": {
                    #     "query_string": {
                    #         "fields": ["title", "description"],
                    #         "query": "*",
                    #         "analyze_wildcard": True
                    #     }
                    # },
                    "filter": {
                        "bool": {
                            "must": [
                                {
                                    "range": {
                                        "published_on": {"format": "epoch_millis",
                                                         "gte": gte,
                                                         "lte": int((datetime.datetime.now() - datetime.timedelta(minutes=60)).strftime('%s')) * 1000
                                                         }
                                    }
                                }
                            ]
                        }
                    }
                }
            },
        }


        return self.request(payload)['hits']['hits']

    def map_response(self, response):
        mapped_response = {
            # '_op_type': 'update',
            "_index": "escucha",
            "_type": "data_items",
            "_id": response["_id"],
            "_source": response["_source"]
        }

        return mapped_response

    def export_json(self):
        size_query = 10000
        length_response = size_query
        length_array = length_response
        gte = 1541030400000  # 01/11/2018
        lte = 1546300799000  # 01/01/2019
        i = 0

        while length_response == size_query and gte < lte:
            # gte += 7200000 #Difference apparently of two hours between the shown date and the processed # Only for production

            response = self.get_escucha(size_query, gte)
            data = map(self.map_response, response)
            length_response = (len(data))
            length_array = length_response

            if length_response == size_query:
                gte = int(datetime.datetime.strptime(
                    data[length_response-1]['_source']['published_on'], '%Y-%m-%d %H:%M:%S').strftime('%s')) * 1000

            with open('db/' + str(gte) + '.json', 'w') as outfile:
                json.dump(data, outfile)
            print(i, ' --> published_on: ', data[length_array-1]
                  ['_source']['published_on'], ',  polarity: ', data[length_array-1]
                  ['_source']['polarity'], '|| NOW ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            i += 1

        print('end')


RemoteModel().export_json()
