# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

from elasticsearch import Elasticsearch
from elasticsearch import helpers

from emotisentiments import SentimentAnalyzer

import langid

from collections import Counter

import datetime
import string
import time

from statsd import StatsClient

from logging.config import dictConfig
import logging


"""
Usar junto con supervisor:

[program:escuchasync]
directory=/home/ubuntu/escucha-informes/
command=/home/ubuntu/escucha-informes/venv/bin/python sync.py
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/escucha/sync_supervisor.log
user=ubuntu
group=ubuntu
"""


"""
curl -XPUT 'http://localhost:9200/escucha'  -H "Content-Type: application/json"  -d '{
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
    "data_items": {
      "properties": {
        "source": {"type": "keyword"},
        "type": {"type": "keyword"},
        "author": {"type": "keyword"},
        "title": {"type": "text", "analyzer": "standard_with_trim"},
        "description": {"type": "text", "analyzer": "standard_with_trim"},
        "published_on": {"type": "date", "format": "YYYY-MM-dd HH:mm:ss"},
        "captured_on": {"type": "date", "format": "YYYY-MM-dd HH:mm:ss"},
        "starts_on": {"type": "date", "format": "YYYY-MM-dd HH:mm:ss"},
        "ends_on": {"type": "date", "format": "YYYY-MM-dd HH:mm:ss"},
        "reason": {"type": "keyword"},
        "geo": {"type": "geo_point"},
        "geoweight": {"type": "float"},
        "accuracy": {"type": "integer"},
        "province": {"type": "keyword"},
        "region": {"type": "keyword"},
        "municipality": {"type": "keyword"},
        "url": {"type": "text", "index" : "false"},
        "polarity": {"type": "float"},
        "author_in_list": {"type": "boolean"},
        "mention_in_list": {"type": "boolean"},
        "hashtags": {"type": "keyword" },
        "mentions": {"type": "keyword" }
      }
    }
  }
}
'
"""

# LOGGING

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s'
        },
    },
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file_escucha': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': '/var/log/escucha/escucha_sync.log',
            'mode': 'a',
            'maxBytes': 524288000, # 500 MB
            'backupCount': 500, # 500 files
        },
        #'mail_admins': {
        #    'level': 'ERROR',
        #    'class': 'logging.handlers.SMTPHandler',
        #    'formatter': 'verbose',
        #    'mailhost': ('smtp.gmail.com', 587),
        #    'fromaddr': '',
        #    'toaddrs': ('',),
        #    'credentials': ('', ''),
        #    'secure': tuple(),
        #    'subject': 'ElasticSearch escucha',
        #},
    },
    'loggers': {
        'escucha': {
            'handlers': ['file_escucha', 'mail_admins'],
            'level': 'DEBUG',
        },
        # Disabled default debug messages for requests module
        'requests': {
        	'handlers': ['null',],
            'level': 'WARNING'
        }
    }
}

dictConfig(LOGGING)
logger = logging.getLogger('escucha')


statsd = StatsClient(prefix='escucha.reports')


class EscuchaSync(object):
	# Constants
	VALID_TWTR_CHARS = u"_@#{0}{1}áéíóúÁÉÍÓÚñÑ".format(string.ascii_letters, string.digits)

	def __init__(self):
		self.es = Elasticsearch('http://localhost:9200')
		self.analyzer = SentimentAnalyzer()
		self.conn = psycopg2.connect(host='remote', database='escucha', user='postgres', password='')
		self.cursor = self.conn.cursor()
                #local solo se usa para datos geograficos, que tambien estan en el remoto
		#self.local_conn = psycopg2.connect(host='localhost', database='escucha', user='postgres', password='')
		#self.local_cursor = self.local_conn.cursor()
		self.local_cursor = self.cursor # =self.conn.cursor()
		self.sources = {}
		self.censored_in_title = []
		self.censored_in_description = []
		self.censored_in_author = []
		self.reload_sources()
		self.reload_censored_keywords()
                self.authors={}
                self.reload_authors()

        def reload_authors(self):
                self.cursor.execute("select name from escucha.follow_hashtags where type='man' and name like '/%' or name like '@%'")
                #self.cursor.execute("select name from escucha.follow_pages")
                self.authors={r[0][1:].lower() for r in self.cursor.fetchall()}

	def reload_sources(self):
		self.cursor.execute("SELECT id, name FROM escucha.sources")
		self.sources = {r[0]: r[1] for r in self.cursor.fetchall()}

	def reload_censored_keywords(self):
		"""
		TODO: Si hay muchas palabras censuradas seria conveniente filtrar todas pero eliminar
		solo las ultimas en cada iteracion del loop
		"""
		self.cursor.execute("SELECT term, in_title, in_description, in_author, blocked_on FROM escucha.blocked_in_reports")
		self.censored_in_title = []
		self.censored_in_description = []
		self.censored_in_author = []
		for r in self.cursor.fetchall():
			term = r[0].lower()
			if r[1]: # In title
				self.censored_in_title.append(term)
			if r[2]: # In description
				self.censored_in_description.append(term)
			if r[3]: # In author
				self.censored_in_author.append(term)

	def has_censored_terms(self, text, censored_list):
		if not text:
			return False
		for kw in censored_list:
			if kw in text.lower():
				return True

	def has_censored_title(self, text):
		return self.has_censored_terms(text, self.censored_in_title)

	def has_censored_description(self, text):
		return self.has_censored_terms(text, self.censored_in_description)

	def has_censored_author(self, text):
		return self.has_censored_terms(text, self.censored_in_author)

	def is_spanish(self, text):
		language, confidence =  langid.classify(text)
		return language == 'es'

	def is_spanish_item(self, title, description):
		if not title and not description:
			return True
		else:
			spanish_item = False
			if title:
				spanish_item = self.is_spanish(title)
			if not spanish_item and description:
				spanish_item = self.is_spanish(description)
			return spanish_item

	def get_geometa(self, lat, lon):
		# name_0: pais, name_1: c.autonoma, name_2: provincia, name_3: region, name_4: municipio
		self.local_cursor.execute("""
			SELECT
				name_2, name_3, name_4
			FROM
				municipios
			WHERE
				ST_CONTAINS(geom, ST_PointFromText('POINT(%s %s)', 4326));
		""", (lon, lat))
		return self.local_cursor.fetchone()

	def get_geoweight(self, lat, lon):
		self.local_cursor.execute("""
			SELECT
				population
			FROM
				municipalities_weight
			WHERE
				ST_CONTAINS(geom, ST_PointFromText('POINT(%s %s)', 4326));
		""", (lon, lat))
		dbres = self.local_cursor.fetchone()
		if dbres is None:
			return None
		else:
			population = dbres[0]
			return 1.0/population if population > 0 else 0

	def twtr_filter(self, text):
		return ''.join(c for c in text if c in self.VALID_TWTR_CHARS)

	def get_twitter_entities(self, text):
		hashtags = []
		mentions = []
		for token in text.split():
			filtered = self.twtr_filter(token)
			if len(filtered) >= 2:
				if filtered.startswith('#'):
					hashtags.append(filtered.lower())
				elif filtered.startswith('@'):
					mentions.append(filtered.lower())
		return hashtags, mentions

	def get_max_captured_on(self):
		# Search max captured_on
		payload = {
			"size": 0,
			"aggs": {
				"max_captured_on": {
					"max": {
						"field": "captured_on"
					}
				}
			}
		}
		r = self.es.search(index="escucha", doc_type="data_items", body=payload)
		es_res = r['aggregations']['max_captured_on']
		if es_res['value'] is None:
			# There are no data in ElasticSearch. Retrieve all
			self.cursor.execute("SELECT min(captured_on) FROM escucha.data_items")
			max_captured_on = self.cursor.fetchone()[0] - datetime.timedelta(days=1)
		else:
			max_captured_on = datetime.datetime.strptime(es_res['value_as_string'], '%Y-%m-%d %H:%M:%S')
		return max_captured_on

	def sync(self):
		logger.info('Sincronizando')

		max_captured_on = self.get_max_captured_on()
		logger.debug('Sincronizando desde %s', max_captured_on)

		self.cursor.execute("""
			DECLARE C CURSOR FOR
				SELECT
					id, source_id, type, author, title, description, published_on, captured_on,
					starts_on, ends_on, reason, geom IS NOT NULL AS is_geom,
					ST_Y(geom) AS lat, ST_X(geom) AS lon, accuracy, url
				FROM
					escucha.data_items
				WHERE
					captured_on > %s
				ORDER BY
					captured_on
		""", (max_captured_on, ))

		logger.info('Indexando')
		last = None
		limit = 5000
		indexados = 0
		n_retrieved = Counter()
		n_items = Counter()
		n_censored = Counter()
		n_notspanish = Counter()
		while not (last is not None and last < limit):
			start_t = time.time()
			self.cursor.execute("FETCH %s FROM C", (limit,))
			batch = self.cursor.fetchall()
			statsd.timing('fetch', (time.time() - start_t)*1000)
			logger.debug('Retrieved items: %s', len(batch))

			actions = []
			n_retrieved.clear()
			n_items.clear()
			n_censored.clear()
			n_notspanish.clear()

			for dbitem in batch:
				source = self.sources[dbitem[1]]
				n_retrieved[source] += 1

				if self.has_censored_title(dbitem[4]) or self.has_censored_description(dbitem[5]) or self.has_censored_author(dbitem[3]):
					n_censored[source] += 1
					continue

				if not self.is_spanish_item(dbitem[4], dbitem[5]):
					n_notspanish[source] += 1
					continue

				n_items[source] += 1

				item = {
					'source': source,
					'type': dbitem[2],
					'author': dbitem[3],
					'title': dbitem[4],
					'description': dbitem[5],
					'published_on': dbitem[6].strftime('%Y-%m-%d %H:%M:%S'),
					'captured_on': dbitem[7].strftime('%Y-%m-%d %H:%M:%S'),
					'starts_on': dbitem[8].strftime('%Y-%m-%d %H:%M:%S') if dbitem[8] is not None else None,
					'ends_on': dbitem[9].strftime('%Y-%m-%d %H:%M:%S') if dbitem[9] is not None else None,
					'reason': dbitem[10],
					'geo': {'lat': dbitem[12], 'lon': dbitem[13]} if dbitem[11] else None,
					'geoweight': None,
					'accuracy': dbitem[14] if dbitem[11] else None,
					'province': None,
					'region': None,
					'municipality': None,
					'url': dbitem[15],
					'polarity': 0,
					'hashtags': [],
					'mentions': [],
				}
				if dbitem[5]:
					item['polarity'] = self.analyzer.polarity(dbitem[5])
					hashtags, mentions = self.get_twitter_entities(dbitem[5])
					item['hashtags'] = hashtags
					item['mentions'] = mentions
				if dbitem[11]:
					geometa = self.get_geometa(dbitem[12], dbitem[13])
					if geometa is not None:
						item['province'] = geometa[0].lower()
						item['region'] = geometa[1].lower()
						item['municipality'] = geometa[2].lower()
					item['geoweight'] = self.get_geoweight(dbitem[12], dbitem[13])
                                if dbitem[3] <> None:
                                    if dbitem[3].lower() in self.authors:
                                        item["author_in_list"]=True 
                                    else:
                                        item["author_in_list"]=False
                                if len(item['mentions'])>0:
                                    cleanmentions=set(x.strip('@/') for x in item['mentions'])
                                    if len(cleanmentions & self.authors) > 0:
                                        item["mention_in_list"]=True
                                    else:
                                        item["mention_in_list"]=False
				action = {
					"_index": "escucha",
					"_type": "data_items",
					"_id": dbitem[0],
					"_source": item
				}
				actions.append(action)

			for source, num in n_retrieved.iteritems():
				statsd.gauge('retrieved_items.%s' % source, num)
			for source, num in n_items.iteritems():
				statsd.gauge('items.%s' % source, num)
			for source, num in n_censored.iteritems():
				statsd.gauge('censored_keywords.%s' % source, num)
			for source, num in n_notspanish.iteritems():
				statsd.gauge('not_spanish.%s' % source, num)

			if actions:
				start_t = time.time()
				helpers.bulk(self.es, actions)
				statsd.timing('bulk', (time.time() - start_t)*1000)
				indexados += len(actions)
				actions = []
				#print '[{0}] {1} items indexados'.format(datetime.datetime.now(), indexados)

			last = len(batch)
		self.cursor.execute("CLOSE C")
		logger.info('%s items indexados', indexados)

	def delete(self):
		logger.info('Eliminando palabras censuradas')
		start_t = time.time()
		payload = {
		  "query": {
		    "bool": {
		      "should": []
		    }
		  }
		}
		for term in self.censored_in_title:
			payload["query"]["bool"]["should"].append({ "match": { "title":  '"' + term + '"'}})
		for term in self.censored_in_description:
			payload["query"]["bool"]["should"].append({ "match": { "description": '"' + term + '"'}})
		for term in self.censored_in_author:
			payload["query"]["bool"]["should"].append({ "match": { "author": term}})
		self.es.delete_by_query(index="escucha", doc_type="data_items", body=payload)
		statsd.timing('delete', (time.time() - start_t)*1000)

	def run(self):
		try:
			logger.info('Iniciado script')
			while True:
				# Every 5 mins
				self.reload_sources()
				self.reload_censored_keywords()
				self.delete()
				self.sync()
				time.sleep(5*60)
		except (SystemExit, KeyboardInterrupt):
			raise
		except:
			logger.error('Unexpected error sync escucha db to elasticsearch', exc_info=True)
		finally:
			logger.info('Finalizado script')


if __name__ == '__main__':
	esync = EscuchaSync()
	esync.run()
