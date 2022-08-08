from django.http import Http404

from main.services import to_epoch

import json
import datetime


def ajax(view_func):
	def _wrapped_view(request, *args, **kwargs):
		"""
		Check if the request is an AJAX request (headers, body,...)
		"""
		if not request.is_ajax(): raise Http404
		return view_func(request, *args, **kwargs)
	return _wrapped_view


def parse_params(view_func):
	def _wrapped_view(request, *args, **kwargs):
		"""
		Parse the AngularJS GET/POST params as arguments of the wrapped function.
		"""
		if request.GET:
			terms = request.GET.getlist('terms', ['*'])
			region = request.GET.get('region', '*').lower()
			start = request.GET.get('start', None)
			end = request.GET.get('end', None)
		else:
			if request.body:
				params = json.loads(request.body)
			else:
				params = {}
			terms = params.get('terms', ['*'])
			region = params.get('region', '*').lower()
			start = params.get('start', None)
			end = params.get('end', None)
		if start:
			start = to_epoch(datetime.datetime.strptime(start, '%d/%m/%Y'))
		if end:
			end = to_epoch(datetime.datetime.strptime(end, '%d/%m/%Y'))
		return view_func(request, terms, region, start, end, *args, **kwargs)
	return _wrapped_view