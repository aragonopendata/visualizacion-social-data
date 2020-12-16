from elasticsearch import Elasticsearch
from elasticsearch import helpers

import datetime
import json

"""
curl -XPUT 'http://biv-aodback-01.aragon.local:9200/anom_escucha'  -H "Content-Type: application/json"  -d '{
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
    "anom_data_items": {
      "properties": {
        "source": {"type": "keyword"},
        "type": {"type": "keyword"},
        "published_on": {"type": "date", "format": "YYYY-MM-dd HH:mm:ss"},
        "geo": {"type": "geo_point"},
        "municipality": {"type": "keyword"},
        "polarity": {"type": "float"},
        "hashtags": {"type": "keyword" },
		"mentions": {"type": "keyword" }
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

    def request_anom(self, payload):
        return self.es.search(index="anom_escucha", doc_type="anom_data_items", body=payload, request_timeout=30)

    def get_escucha(self, size=1, gte=1385855999999, polarity=None):
        payload = {
            "sort": {"published_on": "asc"},
            "size": size,
            "_source": ["source", "type", "published_on", "geo", "municipality", "polarity", "hashtags", "mentions"],
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

            # "aggs": {}
        }

        if(polarity != None):
            payload['query']['bool']['filter']['bool']['must'] = [
                {
                    "range": {
                        "published_on": {"format": "epoch_millis",
                                         "gte": gte,
                                         "lte": gte
                                         }

                    }
                },
                {
                    "range": {
                        "polarity": {
                            "lte": polarity
                        }
                    }
                }
            ]

        return self.request(payload)['hits']['hits']

    def map_response(self, response):
        mapped_response = {
            # '_op_type': 'update',
            "_index": "anom_escucha",
            "_type": "anom_data_items",
            "_id": response["_id"],
            "_source": response["_source"]
        }

        # print mapped_response
        return mapped_response

    # def format_group_week(self):
    #     data = self.get_escucha('w')
    #     actions = []
    #     for week in data:
    #         hashtags = week['total_by_hashtag']['buckets']
    #         hastags_formated = []
    #         for hashtag in hashtags:
    #             hastags_formated.append(
    #                 {'hashtag': hashtag['key'], 'count': hashtag['doc_count']})

    #         item = {'start_week': week['key_as_string'],
    #                 'hashtags': hastags_formated}
    #         action = {
    #             "_index": "weekly_hashtags",
    #             "_type": "weekly_hashtags_items",
    #             "_id": len(actions),
    #             # "_id": "%06d" % (len(actions),),
    #             "_source": item
    #         }

    #         actions.append(action)
    #     # print(actions)
    #     helpers.bulk(self.es, actions)

    def create_anom_escucha(self):
        size_query = 10000
        length_response = size_query
        length_array = length_response
        gte = 1385855999999
        i = 0
        polarity = None
        outfile = open('error_create_anom.txt', 'w')

        while length_response == size_query or polarity != None:
            gte += 7200000 #Difference apparently of two hours between the shown date and the processed # Only for production

            response = self.get_escucha(size_query, gte, polarity)
            data = map(self.map_response, response)
            length_response = (len(data))
            length_array = length_response

            if length_response == size_query or polarity != None:
                gte = int(datetime.datetime.strptime(
                    data[length_response-1]['_source']['published_on'], '%Y-%m-%d %H:%M:%S').strftime('%s')) * 1000

                if(data[0]['_source']['published_on'] == data[length_response-1]['_source']['published_on']):
                    polarity = data[length_response-1]['_source']['polarity']
                    outfile.write(
                        "Repeat at " + data[length_array-1]['_source']['published_on'] + "\n")
                    if(data[0]['_source']['polarity'] == data[length_response-1]['_source']['polarity']):
                        outfile.write(
                            "Overflow at " + data[length_array-1]['_source']['published_on'] +
                            " with polarity equals to" + data[length_array-1]
                            ['_source']['polarity'] + "\n")
                        gte += 1
                        polarity = None
                        length_response = size_query

                else:
                    polarity = None

                if length_response != size_query and polarity != None:
                    gte += 1
                    polarity = None
                    length_response = size_query

                # for record in data:
                #     hashtags = record["_source"]["hashtags"]
                #     if hashtags:
                #         record["_source"]["serialized_hashtags"] = ""
                #         for hashtag in hashtags:
                #             record["_source"]["serialized_hashtags"] += hashtag + " "

                #     mentions = record["_source"]["mentions"]
                #     if mentions:
                #         record["_source"]["serialized_mentions"] = ""
                #         for mention in mentions:
                #             record["_source"]["serialized_mentions"] += mention + " "

            # response = self.get_escucha(size_query, gte)
            # data = map(self.map_response, response

            # with open('get_escucha'+str(gte)+'.json', 'w') as outfile:
            #     json.dump(data, outfile, indent=4)
            helpers.bulk(self.es, data)
            print(i, ' --> published_on: ', data[length_array-1]
                  ['_source']['published_on'], ',  polarity: ', data[length_array-1]
                  ['_source']['polarity'], '|| NOW ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            i += 1

        print(end)


RemoteModel().create_anom_escucha()
