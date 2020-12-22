from __future__ import division

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

    def request_weekly(self, payload):
        return self.es.search(index="weekly_hashtags", doc_type="weekly_hashtags_items", body=payload, request_timeout=30)

    def get_weekly_top_hashtags(self):
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
                                                         # int((datetime.datetime.now() - datetime.timedelta(minutes=60)).strftime('%s')) * 1000
                                                         "lte": 1546300800000
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
                            }
                        }
                    }
                },
            }
        }

        return self.request(payload)['aggregations']['interval']['buckets']

    def get_count_data(self, hashtag, date=None, interval="week", geo=None):
        lte = gte = date
        if interval == 'week':
            lte = int((datetime.datetime.strptime(
                date, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=7)).strftime('%s')) * 1000
            gte = int(datetime.datetime.strptime(
                date, '%Y-%m-%d %H:%M:%S').strftime('%s')) * 1000
        elif interval == 'year':
            # Add a year to the start date
            gte = int(datetime.datetime.strptime(
                date, '%Y-%m-%d %H:%M:%S').strftime('%s')) * 1000
            lte = int((datetime.datetime.strptime(
                date, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=365)).strftime('%s')) * 1000

            # Add a year to the start date
            # gte = int((datetime.datetime.strptime(
            #     date, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(days=179)).strftime('%s')) * 1000
            # lte = int((datetime.datetime.strptime(
            #     date, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=186)).strftime('%s')) * 1000

            # Take the year and create a range between the first and the last day
            # date = datetime.datetime.strptime(
            #     date, '%Y-%m-%d %H:%M:%S')
            # gte = int(datetime.datetime(date.year, 1, 1,
            #                             00, 00, 00).strftime('%s')) * 1000
            # lte = int(datetime.datetime(date.year, 12, 31,
            #                             23, 59, 59).strftime('%s')) * 1000
        else:
            lte = 1385856000000
            gte = int((datetime.datetime.now() -
                       datetime.timedelta(minutes=60)).strftime('%s')) * 1000

        payload = {
            #  "size": 1,
            "query": {
                "bool": {
                    "filter": {
                        "bool": {
                            "must": [
                                {
                                    "range": {
                                        "published_on": {"format": "epoch_millis",
                                                         "gte": gte,
                                                         "lte": lte
                                                         }
                                    }
                                },

                            ]
                        }
                    }
                }
            },
            "aggs": {
                "total_hashtags": {
                    "terms": {
                        "field": "hashtags",
                        "include": [hashtag]
                    }
                }
            }

        }
        if(geo):
            payload["query"]["bool"]["filter"]["bool"]["must"].append({
                "exists":
                {
                    "field": "geo"
                }
            },)

        response = self.request(
            payload)['aggregations']['total_hashtags']['buckets']

        if(response):
            return response[0]['doc_count']
        else:
            return 0

    def data_to_retrieve(self):
        time = 1385856000000  # 01/12/2013
        day = 86400000
        month = day * 30  # 30 days
        size = 10000
        data = []
        time = time + day * 365*4
        queryResults = self.get_escucha(size, time, time + 30*day)
        for queryResult in queryResults:
            # print queryResult["_source"]
            data.append(queryResult["_source"])

        with open('pruebas.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
        # print data

    def analysis_geo(self):
        outfile = open('geo_hashtags_1.txt', 'w')
        outfile.write(
            "Week\tHashtag\tN_T_week\tN_week\t%_week\tN_T_year\tN_year\t%_year\n")

        time_init = datetime.datetime.now()
        data = self.get_weekly_top_hashtags()
        progress = 0
        end_progress = len(data)
        print ("{:0.2f}% progress".format(100 * progress/end_progress))
        for week in data:
            hashtags = week['total_by_hashtag']['buckets']
            for hashtag in hashtags:
                print hashtag
                # print (week['key_as_string'] + "\t" + hashtag['key'])
                outfile.write(week['key_as_string'].encode('utf-8'))
                outfile.write("\t")
                outfile.write(hashtag['key'].encode('utf-8'))
                outfile.write("\t")
                weekly_data_total = self.get_count_data(
                    hashtag['key'], week['key_as_string'], 'week', False)
                outfile.write(str(weekly_data_total))
                outfile.write("\t")
                weekly_data_geo = self.get_count_data(
                    hashtag['key'], week['key_as_string'], 'week', True)
                outfile.write(str(weekly_data_geo))
                outfile.write("\t")
                weekly_data_geo_perc = 100 * weekly_data_geo / weekly_data_total
                outfile.write("{:0.2f}%".format(weekly_data_geo_perc))
                outfile.write("\t")
                yearly_data_total = self.get_count_data(
                    hashtag['key'], week['key_as_string'], 'year', False)
                outfile.write(str(yearly_data_total))
                outfile.write("\t")
                yearly_data_geo = self.get_count_data(
                    hashtag['key'], week['key_as_string'], 'year', True)
                outfile.write(str(yearly_data_geo))
                outfile.write("\t")
                if(yearly_data_total):
                    yearly_data_geo_perc = 100 * yearly_data_geo / yearly_data_total
                else: 
                    yearly_data_geo_perc = 0
                    outfile.write("err-")
                outfile.write("{:0.2f}%".format(yearly_data_geo_perc))
                outfile.write("\n")

            progress = progress + 1
            print ("{:0.2f}% progress".format(100 * progress/end_progress))

        outfile.close()
        print(time_init)
        print(" ---> ")
        print(datetime.datetime.now())


RemoteModel().analysis_geo()
