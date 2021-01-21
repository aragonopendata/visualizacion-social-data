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

    def monthly(self):
        payload = {
            "size": 1000,
            "query": {
                "bool": {
                    "must":                         {
                        "query_string": {
                            # "fields": ["title", "description"],
                            "query": "*",
                            "analyze_wildcard": True
                        },
                    },
                    "filter": {
                        "bool": {
                            "must": [
                                {
                                    "range": {
                                        "published_on": {"format": "epoch_millis",
                                                         "gte": 1385856000000,
                                                         "lte": int((datetime.datetime.now() - datetime.timedelta(minutes=60)).strftime('%s')) * 1000
                                                         }
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            "aggs": {
                "interval": {
                    "date_histogram": {
                        "field": "published_on",
                        "interval": "1M",
                        "time_zone": "+02:00",
                        "min_doc_count": 1,
                    },
                    # "aggs": {
                    #     "total_by_hashtag": {
                    #         "terms": {
                    #             "field": "hashtags",
                    #             "size": size,
                    #             "order": {
                    #                 "_count": "desc"
                    #             }
                    #         },
                    #         "aggs": {

                    #             # "weight_global": {
                    #             #     "value_count": {"field": "author"}
                    #             # },
                    #             "weight_in_list": {
                    #                 "value_count": {"field": "author_in_list"}
                    #             },
                    #             # "weight_total": {
                    #             #     "sum": {
                    #             #         "script": {
                    #             #             "source": "doc._count.value"
                    #             #         }
                    #             #     }
                    #             # }
                    #         }

                    #     },

                    # }
                },
            }

        }
        return self.request(payload)

    def statistics_info(self):
        data = self.monthly()['aggregations']
        with open('estadisticas_meses.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)


RemoteModel().statistics_info()
