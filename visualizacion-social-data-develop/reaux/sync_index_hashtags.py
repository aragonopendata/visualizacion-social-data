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
            "weight_global": { "type": "integer" },
            "weight_in_list": { "type": "integer" },
            "weight_total": { "type": "integer" }
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

    def get_escucha(self, inst=False):
        size = 50
        if inst:
            size = 10

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
                        "interval": "1w",
                        "time_zone": "+02:00",
                        "min_doc_count": 1,
                    },
                    "aggs": {
                        "total_by_hashtag": {
                            "terms": {
                                "field": "hashtags",
                                "size": size,
                                "order": {
                                    "_count": "desc"
                                }
                            },
                            "aggs": {

                                # "weight_global": {
                                #     "value_count": {"field": "author"}
                                # },
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
        if inst:
            payload['query']['bool']['must'] = {
                "bool": {
                    "should": []
                }
            }
            payload["query"]["bool"]["must"]["bool"]["should"].append({
                "match": {
                    "author_in_list": {
                        "query": True,
                    },
                    # "analyze_wildcard": True
                }
            })

        # with open('test.json', 'w') as outfile:
        #     json.dump(self.request(payload)[
        #               'aggregations']['interval']['buckets'], outfile, indent=4)
        return self.request(payload)['aggregations']['interval']

    def format_group_week(self):
        data = self.get_escucha()['buckets']
        actions = []
        data_inst = self.get_escucha(True)['buckets']

        for week in data:
            hashtags_inst =[]
            for week_inst in data_inst:
                if week['key_as_string'] == week_inst['key_as_string']:
                    hashtags_inst = week_inst['total_by_hashtag']['buckets']
            # print week['key']
            hashtags = week['total_by_hashtag']['buckets']
            hastags_formated = []
            for hashtag_inst in hashtags_inst:
                if not any(x['key'] == hashtag_inst['key'] for x in hashtags):
                    hashtags.append(hashtag_inst)
                    # print('anadir ' + hashtag_inst['key'] + ' a la semana ' + week['key_as_string'] )

            for hashtag in hashtags:
                weight_total = hashtag['doc_count'] + \
                    3 * hashtag['weight_in_list']['value']
                hastags_formated.append(
                    {'hashtag': hashtag['key'], 'weight_global': hashtag['doc_count'], 'weight_in_list': hashtag['weight_in_list']['value'], 'weight_total': weight_total})
                # hastags_formated.append(
                #     {'hashtag': hashtag['key'], 'count': hashtag['doc_count']})

            item = {'start_week': week['key_as_string'],
                    'hashtags': hastags_formated}
            action = {
                "_index": "weekly_hashtags",
                "_type": "weekly_hashtags_items",
                "_id": format(len(actions), '05'),
                # "_id": "%06d" % (len(actions),),
                "_source": item
            }

            actions.append(action)
        

        # with open('test.json', 'w') as outfile:
        #     json.dump(actions, outfile, indent=4)
        # with open('test1.json', 'w') as outfile:
        #     json.dump(data, outfile, indent=4)
        # with open('test2.json', 'w') as outfile:
        #     json.dump(data_inst, outfile, indent=4)

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
