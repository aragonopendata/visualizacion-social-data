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

    def request_anom(self, payload):
        return self.es.search(index="anom_escucha", doc_type="anom_data_items", body=payload, request_timeout=1000)

    def request_cloud(self, payload):
        return self.es.search(index="weekly_hashtags", doc_type="weekly_hashtags_items", body=payload, request_timeout=30)

    def count_all(self, index=None):
        payload = {
            "query": {
                "match_all": {}
            },
        }
        if index == None:
            return self.request(payload)['hits']['total']
        elif index == 'anom':
            return self.request_anom(payload)['hits']['total']
        elif index == 'cloud':
            return self.request_cloud(payload)['hits']['total']

    def count_in_list(self):
        payload = {
            "query": {
                "match": {
                    "author_in_list": {
                        "query": True,
                    }
                    #        "analyze_wildcard": True
                }
            }
        }
        return self.request(payload)['hits']['total']

    def historics_cloud(self, query='*', region='*', min_published_on=None, max_published_on=None, size=1):
        payload = {
            "size": 1000,
            "sort": {
                "_id": {
                    "order": "asc"
                }
            },
        }
        return self.request_cloud(payload)['hits']['hits']

    def count_hashtags(self):
        payload = {
            "query": {
                "match": {
                    "author_in_list": {
                        "query": True,
                    }
                    #        "analyze_wildcard": True
                }
            },
            "aggs": {
                "hashtags": {
                    "sum": {
                        "script" : "doc.hashtags.length"
                    }
                }
            }

        }
        return self.request(payload)

    def statistics_info(self):
        total_documents = self.count_all()
        total_in_list = self.count_in_list()
        total_anom_documents = self.count_all('anom')
        total_cloud_weeks = self.count_all('cloud')
        week_cloud = self.historics_cloud()
        total_hashtags = self.count_hashtags()

        print 'Total documents: ', total_documents
        print 'Total in list: ', total_in_list
        print '% instintutional', 100 * \
            (total_in_list * 1.00) / (total_documents * 1.00)
        print 'Total anom documents: ', total_anom_documents
        print 'Total cloud week documents: ', total_cloud_weeks
        print 'Lunes de la primera semana: ', week_cloud[0]['_source']['start_week']
        print 'Lunes de la ultima semana: ', week_cloud[len(
            week_cloud)-1]['_source']['start_week']


RemoteModel().statistics_info()
