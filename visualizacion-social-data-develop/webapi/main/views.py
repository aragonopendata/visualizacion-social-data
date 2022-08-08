from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie, requires_csrf_token
from django.views.decorators.http import require_http_methods

import json
import datetime

from main.models import Subscriptor, Subscription, Term
from main.services import RemoteModel, generate_graph, csv_generator, REGIONS
from main.decorators import ajax, parse_params
from main.jwtauth import create_jwt, required_jwt_auth

remote = RemoteModel()

# TEST!
@ensure_csrf_cookie
def index(request):
	context = {}
	return render(request, 'main/index.html', context)


@require_http_methods(['GET'])
def get_metadata(request):
	response = {
		'regions': REGIONS,
                'mun': sorted([dato['key'] for dato in remote.count_values("municipality")])
	}
	return JsonResponse(response)


@require_http_methods(['POST'])
@parse_params
def get_evol(request, terms, region, start, end):
	response = {
		'evolution': remote.evolution(terms, region, start, end, allow_zeros=True)['aggregations']['evolution']['buckets'],
	}
	return JsonResponse(response)


@require_http_methods(['POST'])
@parse_params
def get_totals(request, terms, region, start, end):
	response = {
		'total_by_source': remote.total_by_field('source', terms, region, start, end)['aggregations']['total_by_field']['buckets'],
		'total_by_type': remote.total_by_field('type', terms, region, start, end)['aggregations']['total_by_field']['buckets'],
		'count': remote.count(terms, region, start, end),
		'count_geo': remote.count_geo(terms, region, start, end),
		'count_authors': remote.count_by_field('author', terms, region, start, end),
		'count_hashtags': remote.count_by_field('hashtags', terms, region, start, end),
		'count_mentions': remote.count_by_field('mentions', terms, region, start, end),
	}
	return JsonResponse(response)


@require_http_methods(['POST'])
@parse_params
def get_tops(request, terms, region, start, end):
	response =  {
		'top_authors': remote.top_by_field('author', terms, region, start, end)['aggregations']['top']['buckets'],
		'top_hashtags': remote.top_by_field('hashtags', terms, region, start, end)['aggregations']['top']['buckets'],
		'top_mentions': remote.top_by_field('mentions', terms, region, start, end)['aggregations']['top']['buckets'],
	}
	return JsonResponse(response)


@require_http_methods(['POST'])
@parse_params
def get_last_items(request, terms, region, start, end):
	params = json.loads(request.body) if request.body else {}
	page = params.get('page', 0)
	is_geo = params.get('is_geo', False)
	size = 50
	response = {
		'last_items': remote.get_last_items(terms, region, start, end, is_geo=is_geo, offset=size*page, size=size)
	}
	return JsonResponse(response)


@require_http_methods(['POST'])
@parse_params
def get_polarity(request, terms, region, start, end):
	polarities = []
	if not isinstance(terms, list):
		terms = [terms]
	for term in terms:
		if term == 'USARLISTA':
			continue
		polarity_info = remote.polarity(term, region, start, end)

		polarities.append({
			'term': term,
			'polarity': polarity_info['aggregations']['polarity']['buckets'],
			'polarity_pos': remote.polarity_mean(term, region, start, end, min_val=0),
			'polarity_neg': -remote.polarity_mean(term, region, start, end, max_val=0),
			'polarity_total': remote.polarity_mean(term, region, start, end),
		})
	response = {
		'polarities': polarities
	}
	return JsonResponse(response)


@require_http_methods(['POST'])
@parse_params
def geogrid(request, terms, region, start, end):
	params = json.loads(request.body) if request.body else {}
	weight = params.get('weight', False)
	response = {
		'geogrid': remote.geogrid(terms, region, start, end, weight)['aggregations']['geogrid']['buckets'],
	}
	return JsonResponse(response)


@require_http_methods(['POST'])
@parse_params
def multiterm_evolution(request, terms, region, start, end):
	evol = []
	for term in terms:
                if term == "USARLISTA":
                   continue
		data = remote.evolution(term, region, start, end, allow_zeros=True)
		evol.append({
			'term': term,
			'data': data['aggregations']['evolution']['buckets']
		})
	response = {
		'evolution': evol,
	}
	return JsonResponse(response)


@require_http_methods(['POST'])
@parse_params
def get_hist_cloud(request, terms, region, start, end):
	response = {
		'historics_cloud': remote.historics_cloud(terms, region, start, end),
	}
	return JsonResponse(response)


@require_http_methods(['POST'])
@parse_params
def get_graph(request, terms, region, start, end):
	params = json.loads(request.body) if request.body else {}
	num_nodes = params.get('num_nodes', 1000)
	es_results = remote.get_last_items(terms, region, start, end, offset=0, size=num_nodes)
	return JsonResponse(generate_graph(es_results))


@require_http_methods(['GET'])
@parse_params
def get_csv(request, terms, region, start, end):
	total = min(remote.count(terms, region, start, end), 20000)
	items = []
	page_size = 5000
	page = 0
	while len(items) < total:
		items.extend(remote.get_last_items(terms, region, start, end, offset=page_size*page, size=page_size))
		page += 1
	response = StreamingHttpResponse(csv_generator(items), content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="aosd.csv"'
	return response



# SUBSCRIPTIONS
###############

@require_http_methods(['POST'])
@required_jwt_auth
def subscribe(request):
	# Parse the AngularJS params
	if request.body:
		params = json.loads(request.body)
	else:
		return JsonResponse({'status': 'nok', 'error': 'Invalid request'}, status=400)
	subscriptions = params.get('subscriptions', [])

	request.subscriptor.subscriptions.all().delete()
	for subt in subscriptions:
		if not subt['terms']:
			return JsonResponse({'status': 'nok', 'error': 'Empty subscription'}, status=400)
		new_sub = Subscription.objects.create(subscriptor=request.subscriptor, name=subt['name'], region=subt['region'])
		for term in subt['terms']:
			Term.objects.create(subscription=new_sub, term=term)
	return JsonResponse({'status': 'ok'})


@require_http_methods(['GET'])
@required_jwt_auth
def get_subscriptions(request):
	subscriptions = []
	for subt in request.subscriptor.subscriptions.all():
		subscriptions.append({
			'name': subt.name,
			'region': subt.region,
			'terms': [t.term for t in subt.terms.all()],
		})
	return JsonResponse({'status': 'ok', 'subscriptions': subscriptions})


@require_http_methods(['DELETE'])
@required_jwt_auth
def cancel_subscription(request):
	request.subscriptor.delete()
	return JsonResponse({'status': 'ok'})
