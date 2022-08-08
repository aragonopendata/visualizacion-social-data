# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch

import Geohash

import datetime
import calendar

import sys
import os
import re

from collections import defaultdict

import csv
from cStringIO import StringIO

from django.conf import settings

sys.path.append(os.path.realpath(os.path.join(
    settings.PARENT_DIR, os.pardir, 'core')))
# import kampalGraph as KG
# import igraph

TMPLOGFILE = '/tmp/kmplelasticlog.txt'

REGIONS = [
    'Alto Gállego',
    'Andorra - Sierra de Arcos',
    'Aranda',
    'Bajo Aragón',
    'Bajo Aragón - Caspe',
    'Bajo Cinca',
    'Bajo Martín',
    'Campo de Belchite',
    'Campo de Borja',
    'Campo de Cariñena',
    'Campo de Daroca',
    'Cinca Medio',
    'Cinco Villas',
    'Comunidad de Calatayud',
    'Comunidad de Teruel',
    'Cuencas Mineras',
    'Gúdar - Javalambre',
    'Hoya de Huesca',
    'Jiloca',
    'La Jacetania',
    'La Litera',
    'La Ribagorza',
    'Los Monegros',
    'Maestrazgo',
    'Matarraña',
    'Ribera Alta del Ebro',
    'Ribera Baja del Ebro',
    'Sierra de Albarracín',
    'Sobrarbe',
    'Somontano de Barbastro',
    'Tarazona y El Moncayo',
    'Valdejalón',
    'Zaragoza',
]
provincia = {'PROV HUESCA': 'huesca',
             'PROV TERUEL': 'teruel', 'PROV ZARAGOZA': 'zaragoza'}


def to_epoch(date):
    return calendar.timegm(date.timetuple()) * 1000


class RemoteModel(object):
    def __init__(self):
        self.es = Elasticsearch(
            'http://biv-aodback-01.aragon.local:9200', retry_on_timeout=True)

    def request(self, payload):
        with open(TMPLOGFILE, 'w+') as f:
            print >>f, "ELASTIC", payload
        return self.es.search(index="escucha", doc_type="data_items", body=payload)

    def count_values(self, field):
        payload = {
            "query": {
                "bool": {
                    "should": [
                        {"term": {"province": "zaragoza"}},
                        {"term": {"province": "huesca"}},
                        {"term": {"province": "teruel"}}
                    ]}
            },
            "aggs": {
                "total": {
                    "terms": {
                        "field": field,
                        "size": 1000
                    }
                }
            }
        }
        return self.request(payload)['aggregations']['total']['buckets']

    def request_cloud(self, payload):
        with open(TMPLOGFILE, 'w+') as f:
            print >>f, "ELASTIC_CLOUD", payload
        return self.es.search(index="weekly_hashtags", doc_type="weekly_hashtags_items", body=payload)

    def request_anom(self, payload):
        with open(TMPLOGFILE, 'w+') as f:
            print >>f, "ELASTIC_ANOM", payload
        return self.es.search(index="anom_escucha", doc_type="anom_data_items", body=payload)

    def _add_region(self, payload, region):
        if region != '*':
            if region.upper() in provincia:
                payload['query']['bool']['filter']['bool']['must'].append(
                    {
                        "term": {
                            "province": provincia[region.upper()]
                        }
                    }
                )
            elif region.upper().startswith('MUN '):
                payload['query']['bool']['filter']['bool']['must'].append(
                    {
                        "term": {
                            "municipality": region[4:].lower()
                        }
                    }
                )
            else:
                payload['query']['bool']['filter']['bool']['must'].append(
                    {
                        "term": {
                            "region": region
                        }
                    }
                )

    def _add_theme(self, payload, query):
        payload['query']['bool']['must'] = {
            "bool": {
                "should": []
            }
        }
        if isinstance(query, list):
            terms = query
        elif isinstance(query, basestring):
            terms = [query]
        else:
            raise ValueError('Invalid query')
        if not('USARLISTA' in terms):
            raise ValueError('Invalid query')
        for term in terms:
            if term == 'USARLISTA':
                payload["query"]["bool"]["filter"]["bool"]["must"].append({
                    "match": {
                        "author_in_list": {
                            "query": True,
                        }
                        #        "analyze_wildcard": True
                    }
                })
                continue
            if term != '*':
                term = '"' + term + '"'
            payload["query"]["bool"]["must"]["bool"]["should"].append({
                "query_string": {
                    "fields": ["title", "description"],
                    "query": term,
                    "analyze_wildcard": True
                }
            })

    def _add_theme_anom(self, payload, query):
        payload['query']['bool']['must'] = {
            "bool": {
                "should": []
            }
        }
        if isinstance(query, list):
            terms = query
        elif isinstance(query, basestring):
            terms = [query]
        else:
            raise ValueError('Invalid query')
        # if not('USARLISTA' in terms):
        # 	raise ValueError('Invalid query')
        for term in terms:
            if term == 'USARLISTA':
                #    payload["query"]["bool"]["filter"]["bool"]["must"].append({
                #         "match": {
                #              "author_in_list": {
                #                 "query": True,
                #                  }
                #         #        "analyze_wildcard": True
                #         }
                #    })
                continue
            if term != '*':
                term = '#' + term + ''

            payload["query"]["bool"]["must"]["bool"]["should"].append({
                "query_string": {
                    "fields": ["hashtags"],
                    "query": term,
                    "analyze_wildcard": True
                }
            })

    @property
    def _default_min_published_on(self):
        return 1385856000000

    @property
    def _default_max_published_on(self):
        return int((datetime.datetime.now() - datetime.timedelta(minutes=60)).strftime('%s')) * 1000

    def evolution(self, query='*', region='*', min_published_on=None, max_published_on=None, allow_zeros=False):
        payload = {
            "size": 1000,
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            #   "fields": ["title", "description"],
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
                                                       #   "gte": min_published_on or self._default_min_published_on,
                                                       #   "lte": max_published_on or self._default_max_published_on
                                                       }
                                  }
                              }
                            ]
                        }
                    }
                }
            },
            "aggs": {
                "evolution": {
                    "date_histogram": {
                        "field": "published_on",
                        "interval": "1w",
                        "time_zone": "+02:00",
                        "min_doc_count": 1,
                        "extended_bounds": {
                            "min": min_published_on or self._default_min_published_on,
                            "max": max_published_on or self._default_max_published_on
                        }
                    },
                }
            }
        }
        if allow_zeros:
            payload["aggs"]["evolution"]["date_histogram"]["min_doc_count"] = 0
        # self._add_theme(payload, query)
        self._add_theme_anom(payload, query)
        self._add_region(payload, region)
        # return self.request(payload)
        return self.request_anom(payload)

    def total_by_field(self, field, query='*', region='*', min_published_on=None, max_published_on=None):
        payload = {
            "size": 1000,
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            #   "fields": ["title", "description"],
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
                                                       "gte": min_published_on or self._default_min_published_on,
                                                       "lte": max_published_on or self._default_max_published_on
                                                       }
                                  }
                              }
                            ]
                        }
                    }
                }
            },
            "aggs": {
                "total_by_field": {
                    "terms": {
                        "field": field,
                        "size": 50,
                        "order": {
                            "_count": "desc"
                        }
                    }
                }
            }
        }
        # self._add_theme(payload, query)
        self._add_theme_anom(payload, query)
        self._add_region(payload, region)
        # return self.request(payload)
        return self.request_anom(payload)

    def count(self, query='*', region='*', min_published_on=None, max_published_on=None):
        payload = {
            "size": 1000,
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            #   "fields": ["title", "description"],
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
                                                       "gte": min_published_on or self._default_min_published_on,
                                                       "lte": max_published_on or self._default_max_published_on
                                                       }
                                  }
                              }
                            ]
                        }
                    }
                }
            },
            "aggs": {}
        }
        # self._add_theme(payload, query)
        self._add_theme_anom(payload, query)
        self._add_region(payload, region)
        # return self.request(payload)['hits']['total']
        return self.request_anom(payload)['hits']['total']

    def count_geo(self, query='*', region='*', min_published_on=None, max_published_on=None):
        payload = {
            "size": 1000,
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            #   "fields": ["title", "description"],
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
                                                       "gte": min_published_on or self._default_min_published_on,
                                                       "lte": max_published_on or self._default_max_published_on
                                                       }
                                  }
                              },
                                {
                                  "exists": {
                                      "field": "geo"
                                  }
                              },
                            ]
                        }
                    }
                }
            },
            "aggs": {}
        }
        # self._add_theme(payload, query)
        self._add_theme_anom(payload, query)
        self._add_region(payload, region)
        # return self.request(payload)['hits']['total']
        return self.request_anom(payload)['hits']['total']

    def geogrid(self, query='*', region='*', min_published_on=None, max_published_on=None, weight=False):
        payload = {
            "size": 1000,
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            #   "fields": ["title", "description"],
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
                                                       "gte": min_published_on or self._default_min_published_on,
                                                       "lte": max_published_on or self._default_max_published_on
                                                       }
                                  }
                              }
                            ]
                        }
                    }
                }
            },
            "aggs": {
                "geogrid": {
                    "geohash_grid": {
                        "field": "geo",
                        "precision": 6
                    }
                }
            }
        }
        if weight:
            payload['aggs']['geogrid']['aggs'] = {
                "weight": {
                    "sum": {
                        "field": "geoweight"
                    }
                }
            }
        # self._add_theme(payload, query)
        self._add_theme_anom(payload, query)
        self._add_region(payload, region)
        # geogrid = self.request(payload)
        geogrid = self.request_anom(payload)
        for row in geogrid['aggregations']['geogrid']['buckets']:
            lat, lon, _, _ = Geohash.decode_exactly(row['key'])
            row['lat'] = lat
            row['lon'] = lon
        return geogrid

    def polarity(self, query='*', region='*', min_published_on=None, max_published_on=None):
        payload = {
            "size": 1000,
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            #   "fields": ["title", "description"],
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
                                                       "gte": min_published_on or self._default_min_published_on,
                                                       "lte": max_published_on or self._default_max_published_on
                                                       }
                                  }
                              }
                            ]
                        }
                    }
                }
            },
            "aggs": {
                "polarity": {
                    "range": {
                        "field": "polarity",
                        "ranges": [
                            {
                                "key": "negative",
                                "from": -1,
                                "to": -0.1
                            },
                            {
                                "key": "neutral",
                                "from": -0.1,
                                "to": 0.1
                            },
                            {
                                "key": "positive",
                                "from": 0.1,
                                "to": 1
                            }
                        ],

                        "keyed": True
                    }, 
                    "aggs": {
                        "stats": {"extended_stats": {"field": "polarity"}}
                    },
                },
            }
        }

        # self._add_theme(payload, query)
        self._add_theme_anom(payload, query)
        self._add_region(payload, region)
        # return self.request(payload)
        return self.request_anom(payload)

    def polarity_mean(self, query='*', region='*', min_published_on=None, max_published_on=None, min_val=None, max_val=None):
        payload = {
            "size": 1000,
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            #   "fields": ["title", "description"],
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
                                                       "gte": min_published_on or self._default_min_published_on,
                                                       "lte": max_published_on or self._default_max_published_on
                                                       }
                                  }
                              }
                            ]
                        }
                    }
                }
            },
            "aggs": {
                "sum_vals": {
                    "sum": {
                        "field": "polarity"
                    }
                }
            }
        }
        if min_val is not None or max_val is not None:
            range_polarity = {"range": {"polarity": {}}}
            if min_val is not None:
                range_polarity["range"]["polarity"]["gt"] = min_val
            if max_val is not None:
                range_polarity["range"]["polarity"]["lt"] = max_val
            payload["query"]["bool"]["filter"]["bool"]["must"].append(
                range_polarity)
        # self._add_theme(payload, query)
        self._add_theme_anom(payload, query)
        self._add_region(payload, region)
        # res = self.request(payload)
        res = self.request_anom(payload)

        if res["hits"]["total"] > 0:
            return float(res["aggregations"]["sum_vals"]["value"]) / float(res["hits"]["total"])
        else:
            return 0.0

    def top_by_field(self, field, query='*', region='*', min_published_on=None, max_published_on=None, top=50):
        payload = {
            "size": 1000,
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            #   "fields": ["title", "description"],
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
                                                       "gte": min_published_on or self._default_min_published_on,
                                                       "lte": max_published_on or self._default_max_published_on
                                                       }
                                  }
                              }
                            ]
                        }
                    }
                }
            },
            "aggs": {
                "top": {
                    "terms": {
                        "field": field,
                        "size": top,
                        "order": {
                            "_count": "desc"
                        }
                    }
                }
            }
        }
        self._add_theme(payload, query)
        # self._add_theme_anom(payload, query)
        self._add_region(payload, region)
        return self.request(payload)
        # return self.request_anom(payload)

    def count_by_field(self, field, query='*', region='*', min_published_on=None, max_published_on=None):
        payload = {
            "size": 1000,
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            #   "fields": ["title", "description"],
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
                                                       "gte": min_published_on or self._default_min_published_on,
                                                       "lte": max_published_on or self._default_max_published_on
                                                       }
                                  }
                              }
                            ]
                        }
                    }
                }
            },
            "aggs": {
                "total": {
                    "cardinality": {
                        "field": field
                    }
                }
            }
        }
        # self._add_theme(payload, query)
        self._add_theme_anom(payload, query)
        self._add_region(payload, region)
        # return self.request(payload)['aggregations']['total']['value']
        return self.request_anom(payload)['aggregations']['total']['value']

    def get_last_items(self, query='*', region='*', min_published_on=None, max_published_on=None, is_geo=False, offset=0, size=50):
        payload = {
            "from": offset,
            "size": size,
            "sort": {
                "published_on": "desc"
            },
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
                                                       "gte": min_published_on or self._default_min_published_on,
                                                       "lte": max_published_on or self._default_max_published_on
                                                       }
                                  }
                              }
                            ]
                        }
                    }
                }
            },
            "aggs": {}
        }
        if is_geo:
            payload['query']['bool']['filter']['bool']['must'].append({
                "exists": {"field": "geo"}
            })
        self._add_theme(payload, query)
        # self._add_theme_anom(payload, query)
        self._add_region(payload, region)
        hits = self.request(payload)['hits']['hits']
        # hits = self.request_anom(payload)['hits']['hits']
        results = []
        for hit in hits:
            item = hit['_source']
            item['id'] = hit['_id']
            results.append(item)
        return results

    def historics_cloud(self, query='*', region='*', min_published_on=None, max_published_on=None, size=1):
        payload = {
            "size": size,
            "sort": {
                "_id": {
                    "order": "asc"
                }
            },
            "query": {
                "bool": {
                    "filter": {
                        "bool": {
                            "must": [{
                                "range": {
                                    "start_week": {
                                        "format": "epoch_millis",
                                        "gte": min_published_on or self._default_min_published_on,
                                        "lte": max_published_on or self._default_max_published_on
                                    }
                                }
                            }]
                        }
                    }
                }
            }
        }
        return self.request_cloud(payload)['hits']['hits']


def generate_graph(es_search):
    if len(es_search) == 0:
        return {'nodes': [], 'edges': []}

    nodes = set()  # Avoid duplicates
    graph = defaultdict(lambda: defaultdict(int))
    p = re.compile('\s(@\w+)\s')
    for result in es_search:
        description = result['description']
        author = result['author']
        source = result['source']
        if description is None or author is None or len(author.split()) == 0:
            continue

        if source == 'twitter':
            author = '@' + author
        author = author.lower()
        nodes.add(author)

        matches = p.findall(description.lower())
        for match in matches:
            nodes.add(match)
            graph[author][match] += 1

    g = KG.KampalGraph()
    g["name"] = "name"
    g["selection"] = "selection"
    g['type'] = ''
    g['year'] = ''

    for node in nodes:
        g.add_vertex(label=node, name=node, surname_1=node, sex='')

    for source in graph.keys():
        for target in graph[source].keys():
            g.add_edge(source, target, acum_weight=graph[source][target])

    g.simplify(loops=False, combine_edges=dict(acum_weight="sum"))
    g.vs['weight'] = g.strength(
        g.vs, weights=g.es["acum_weight"], mode=igraph.IN)
    g.setNetworkProperties()
    g.setLayout(steps=1000, exp_repulser=4.1)
    g.setSize()
    g.collisions()
    g.setCommunity()
    g.setColorNodes()
    g.setColorEdges()
    return g.toJSON(serialize_nodes=True, serialize_edges=True)


def csv_generator(items):
    """ Python generator to generate a csv without save all in memory. """
    def get_raw_data(buff):
        buff.seek(0)
        data = buff.read()
        buff.seek(0)
        buff.truncate()
        return data

    buff = StringIO()
    writer = csv.writer(buff)
    writer.writerow(['id', 'source', 'type', 'title', 'description', 'author',
                     'published_on', 'starts_on', 'ends_on', 'latitude', 'longitude', 'url'])
    yield get_raw_data(buff)
    for item in items:
        writer.writerow([
            item['id'],
            item['source'],
            item['type'],
            item['title'].encode('utf8') if item['title'] else '',
            item['description'].encode('utf8') if item['description'] else '',
            item['author'].encode('utf8') if item['author'] else '',
            item['published_on'],
            item['starts_on'],
            item['ends_on'],
            item['geo']['lat'] if item['geo'] else '',
            item['geo']['lon'] if item['geo'] else '',
            item['url'].encode('utf8'),
        ])
        yield get_raw_data(buff)
