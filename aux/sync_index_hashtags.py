from elasticsearch import Elasticsearch
from elasticsearch import helpers

import datetime
import json

"""
curl -XPUT 'http://biv-aodback-01.aragon.local:9200/weekly_hashtags'  -H "Content-Type: application/json"  -d '{
  "settings": {
    "analysis": {
      "analyzer": {
        "standard_with_trim": {
          "tokenizer": "standard",
          "filter": ["lowercase", "stop", "trim"]
        }
      }
    }
  },
  "mappings": {
    "weekly_hashtags_items": {
      "properties": {
        "start_week": {"type": "date", "format": "YYYY-MM-dd HH:mm:ss"},
        "hashtags": {
          "properties": {
            "hashtag": {"type": "keyword"},
            "count": {"type": "integer"}
          }
        }
      }
    }
  }
}
'
"""


class RemoteModel(object):
    def __init__(self):
        self.es = Elasticsearch(
            'http://biv-aodback-01.aragon.local:9200', retry_on_timeout=True)

    def request(self, payload):
        # with open("/tmp/elasticlog.txt", 'w+') as f:
        #     print >>f, "ELASTIC", payload
        return self.es.search(index="escucha", doc_type="data_items", body=payload, request_timeout=30)

    def request_weekly(self, payload):
        return self.es.search(index="weekly_hashtags", doc_type="weekly_hashtags_items", body=payload, request_timeout=30)

    def get_escucha(self):
        payload = {
            "size": 1000,
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            # "fields": ["title", "description"],
                            "query": "*",
                            "analyze_wildcard": True
                        },
                        # "match": {
                        #     "author_in_list": {
                        #         "query": True,
                        #     }
                        #     #        "analyze_wildcard": True
                        # }
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
                        "interval": "1w",
                        "time_zone": "+02:00",
                        "min_doc_count": 1,
                    },
                    "aggs": {
                        "total_by_hashtag": {
                            "terms": {
                                "field": "hashtags",
                                "size": 50,
                                "order": {
                                    "_count": "desc"
                                }
                            },
                            "aggs": {

                                "weight_global": {
                                    "value_count": {"field": "author"}
                                },
                                "weight_in_list": {
                                    "value_count": {"field": "author_in_list"}
                                },
                                # "weight_total": {
                                #     "sum": {
                                #         "script": {
                                #             "source": "doc._count.value"
                                #         }
                                #     }
                                # }
                            }

                        },

                    }
                },
            }
        }
        with open('test.json', 'w') as outfile:
            json.dump(self.request(payload)[
                      'aggregations']['interval']['buckets'], outfile, indent=4)
        # return self.request(payload)['aggregations']['interval']['buckets']

    def format_group_week(self):
        data = self.get_escucha()
        actions = []
        for week in data:
            hashtags = week['total_by_hashtag']['buckets']
            hastags_formated = []
            for hashtag in hashtags:
                hastags_formated.append(
                    {'hashtag': hashtag['key'], 'count': hashtag['doc_count']})

            item = {'start_week': week['key_as_string'],
                    'hashtags': hastags_formated}
            action = {
                "_index": "weekly_hashtags",
                "_type": "weekly_hashtags_items",
                "_id": len(actions),
                # "_id": "%06d" % (len(actions),),
                "_source": item
            }

            actions.append(action)
        # print(actions)
        helpers.bulk(self.es, actions)

    def get_from_weekly_hashtags(self):
        payload = {
            "size": 1,
            # "sort": {
            #     "_id": "asc"
            # },
            # "query": {
            #     "bool": {
            #         "filter": {
            #             "bool": {
            #                 "must": [{
            #                     "range": {
            #                         "start_week": {
            #                             "format": "epoch_millis",
            #                              "gte": 1515970800000, #15/01/2018
            #                              "lte": 1517266800000 #30/01/2018
            #                         }
            #                     }
            #                 }]
            #             }
            #         }
            #     }
            # }
        }

        print(self.request_weekly(payload)['hits']['hits'])

    def sync_weekly_hashtags(self):
        self.format_group_week()  # En teoria ya creado el indice
        # self.get_from_weekly_hashtags()


RemoteModel().sync_weekly_hashtags()
