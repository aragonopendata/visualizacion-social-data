from elasticsearch import Elasticsearch
from elasticsearch import helpers

import datetime


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

    def get_from_escucha(self):
        payload = {
            "size": 1000,
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            "fields": ["title", "description"],
                            "query": "*",
                            "analyze_wildcard": True
                        }
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
                "weekly": {
                    "date_histogram": {
                        "field": "published_on",
                        "interval": "1w",
                        "time_zone": "+02:00",
                        "min_doc_count": 1,
                        # "extended_bounds": {  # Por algun motivo no hace nada
                        #     "min": 1598824800000,
                        #     "max": 1598824800000
                        # }
                    },
                    "aggs": {
                        "total_by_hashtag": {
                            "terms": {
                                "field": "hashtags",
                                "size": 50,
                                "order": {
                                    "_count": "desc"
                                }
                            }
                        }
                    }
                },
            }
        }
        return self.request(payload)['aggregations']['weekly']['buckets']

    def format_group_week(self, data):
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
                "_id": "%06d" % (len(actions),),
                "_source": item
            }

            actions.append(action)
        # print(actions)
        helpers.bulk(self.es, actions)

    def get_from_weekly_hashtags(self):
        payload = {
            "size": 1000,
            "sort": {
                "_id": "asc"
            },
            "query": {
                'match_all': {}
                # "bool": {
                #     "filter": {
                #         "bool": {
                #             "must": [
                #                 {
                #                     "range": {
                #                         # "_id":{
                #                         #     "gte": 1496095200000, #01/08/2018
                #                         #                    "lte": 1533679200000 #08/08/2018
                #                         # }
                #                         "start_week": {"format": "epoch_millis",
                #                                           "gte": 1496095200000, #01/08/2018
                #                                           "lte": 1533679200000 #08/08/2018
                #                                        }
                #                     }
                #                 }
                #             ]
                #         }
                #     }
                # }
            }
        }

        print(self.request_weekly(payload)['hits']['hits'])

    def format_group_day(self, data):
        formated = []
        for week in data:
            hashtags = week['total_by_hashtag']['buckets']
            for hashtag in hashtags:
                formated.append(
                    {'start_week': week['key_as_string'], 'hashtag': hashtag['key'], 'count': hashtag['doc_count']})

        print(formated)

    def sync_weekly_hashtags(self):
        # data = self.get_from_escucha()
        # self.format_group_week(data)  # En teoria ya creado el indice
        # self.format_group_day(data)
        self.get_from_weekly_hashtags()


RemoteModel().sync_weekly_hashtags()
