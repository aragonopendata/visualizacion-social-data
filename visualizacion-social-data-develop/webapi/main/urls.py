from django.conf.urls import include, url

from main import views, jwtauth

urlpatterns = [#'',
	# Test
	url(r'^$', views.index, name='index'),

	# Data
	url(r'^get_metadata/$', views.get_metadata, name='get_metadata'),
	url(r'^get_evol/$', views.get_evol, name='get_evol'),
	url(r'^get_hist_cloud/$', views.get_hist_cloud, name='get_hist_cloud'),
	url(r'^get_totals/$', views.get_totals, name='get_totals'),
	url(r'^get_tops/$', views.get_tops, name='get_tops'),
	url(r'^get_polarity/$', views.get_polarity, name='get_polarity'),
	url(r'^geogrid/$', views.geogrid, name='geogrid'),
	url(r'^get_last_items/$', views.get_last_items, name='get_last_items'),
	url(r'^multiterm_evolution/$', views.multiterm_evolution, name='multiterm_evolution'),
	url(r'^get_graph/$', views.get_graph, name='get_graph'),
	url(r'^get_csv/$', views.get_csv, name='get_csv'),

	# Subscriptions
	url(r'^register/$', jwtauth.register, name='jwt_register'),
	url(r'^auth/$', jwtauth.auth, name='jwt_auth'),
	url(r'^password_change/$', jwtauth.password_change, name='jwt_password_change'),
	url(r'^password_reset/$', jwtauth.password_reset, name='jwt_password_reset'),
	url(r'^password_reset_confirm/$', jwtauth.password_reset_confirm, name='jwt_password_reset_confirm'),
	url(r'^subscribe/$', views.subscribe, name='subscribe'),
	url(r'^get_subscriptions/$', views.get_subscriptions, name='get_subscriptions'),
	url(r'^cancel_subscription/$', views.cancel_subscription, name='cancel_subscription'),
]
