# -*- coding: utf-8 -*-
from django.test import TestCase
from django.http import HttpRequest, JsonResponse
from django.conf import settings
from django.core import mail

from mock import Mock

import json

import jwt
import base64

from main.models import Subscriptor, Subscription, Term, InvalidCredentials, login
from main.jwtauth import validate_jwt, required_jwt_auth, token_generator


class TestSubscriptor(TestCase):
	def setUp(self):
		Subscriptor.objects.all().delete()

	def test_create_subscriptor(self):
		subs = Subscriptor.objects.create_subscriptor('me@me.com', 'pass')
		self.assertEqual(Subscriptor.objects.count(), 1)
		with self.assertRaises(ValueError):
			Subscriptor.objects.create_subscriptor('', 'pass')
		with self.assertRaises(ValueError):
			Subscriptor.objects.create_subscriptor('me@to.com', '')
		with self.assertRaises(ValueError):
			Subscriptor.objects.create_subscriptor('', '')

	def test_dup_email(self):
		subs = Subscriptor.objects.create_subscriptor('me@me.com', 'pass')
		with self.assertRaises(ValueError):
			Subscriptor.objects.create_subscriptor('me@me.com', 'pass2')

	def test_login(self):
		subs = Subscriptor.objects.create_subscriptor('me@me.com', 'pass')
		self.assertEqual(login('me@me.com', 'pass'), subs)
		with self.assertRaises(InvalidCredentials):
			login('me@me.com', 'nopass')
		with self.assertRaises(InvalidCredentials):
			login('me@te.com', 'pass')
		with self.assertRaises(InvalidCredentials):
			login('me@me.com', '')
		with self.assertRaises(InvalidCredentials):
			login('', 'pass')
		with self.assertRaises(InvalidCredentials):
			login('', '')

	def test_change_password(self):
		subs = Subscriptor.objects.create_subscriptor('me@me.com', 'pass')
		subs.change_password('pass', 'new_pass')
		self.assertEqual(login('me@me.com', 'new_pass'), subs)
		with self.assertRaises(InvalidCredentials):
			login('me@me.com', 'pass')
		self.assertFalse(subs.change_password('err', 'new_new_pass'))


class TestSubscription(TestCase):
	def setUp(self):
		Term.objects.all().delete()
		Subscription.objects.all().delete()
		Subscriptor.objects.all().delete()

	def test_create_subscription(self):
		subs = Subscriptor.objects.create_subscriptor('me@me.com', 'pass')
		subt = Subscription.objects.create(subscriptor=subs, name='test', region='*')
		self.assertEqual(subs.subscriptions.first(), subt)

	def test_create_term(self):
		subs = Subscriptor.objects.create_subscriptor('me@me.com', 'pass')
		subt = Subscription.objects.create(subscriptor=subs, name='test', region='*')
		term = Term.objects.create(subscription=subt, term='myterm')
		self.assertEqual(subs.subscriptions.first(), subt)
		self.assertEqual(subt.terms.first(), term)


class TestJWT(TestCase):
	def setUp(self):
		Subscriptor.objects.all().delete()

	def test_register(self):
		# Valid register
		payload = {
			'email': 'ext@ext.net',
 			'password': 'topsecret',
		}
		response = self.client.post('/register/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 200)
		self.assertJSONEqual(response.content, {'status': 'ok'})

		self.assertTrue(Subscriptor.objects.filter(email='ext@ext.net').exists())

		# No credentials
		payload = {}
		response = self.client.post('/register/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 400)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid request'})

		# Repeated email
		payload = {
			'email': 'ext@ext.net',
			'password': 'topsecret',
		}
		response = self.client.post('/register/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 400)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'The email is yet registered'})

	def test_auth(self):
		subs = Subscriptor.objects.create_subscriptor('me@me.com', 'pass')

		# Valid credentials
		payload = {'email': 'me@me.com', 'password': 'pass'}
		response = self.client.post('/auth/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 200)
		expected_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJoIjoiMWNhYTZhODg4NWJjMmYwNDQyYmRiMDY4MTVlMzE3NjU0NWE4YjhkNjM4MjJjODUxZDgxNWM1Y2IxYzJlZjAxNCIsInNpZCI6MX0.eu79E8W3p5H8CQkg-z1AK58BmjRAw_Rk8OP-UPvaf20'
		self.assertJSONEqual(response.content, {'status': 'ok',	'jwt_token': expected_token})
		self.assertTrue(response.has_header('JWT_TOKEN'))
		self.assertEqual(response._headers['jwt_token'][1], expected_token)

		# Invalid credentials
		payload = {'email': 'me@me.com', 'password': 'pass2'}
		response = self.client.post('/auth/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 403)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid credentials'})
		self.assertFalse(response.has_header('JWT_TOKEN'))

		payload = {'email': 'me@me2.com', 'password': 'pass'}
		response = self.client.post('/auth/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 403)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid credentials'})
		self.assertFalse(response.has_header('JWT_TOKEN'))

		payload = {'password': 'pass'}
		response = self.client.post('/auth/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 403)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid credentials'})
		self.assertFalse(response.has_header('JWT_TOKEN'))

		payload = {'email': 'me@me.com'}
		response = self.client.post('/auth/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 403)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid credentials'})
		self.assertFalse(response.has_header('JWT_TOKEN'))

		payload = {}
		response = self.client.post('/auth/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 403)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid credentials'})
		self.assertFalse(response.has_header('JWT_TOKEN'))

	def test_validate(self):
		subs = Subscriptor.objects.create_subscriptor('me@me.com', 'pass')

		payload = {'email': 'me@me.com', 'password': 'pass'}
		response = self.client.post('/auth/', json.dumps(payload), content_type="application/json")
		jwt_token = json.loads(response.content)['jwt_token']

		self.assertEqual(validate_jwt(jwt_token), subs)

		invalid_token = 'none'
		with self.assertRaises(jwt.DecodeError):
			validate_jwt(invalid_token)

	def test_required_jwt_auth_decorator(self):
		subs = Subscriptor.objects.create_subscriptor('me@me.com', 'pass')

		payload = {'email': 'me@me.com', 'password': 'pass'}
		response = self.client.post('/auth/', json.dumps(payload), content_type="application/json")
		jwt_token = json.loads(response.content)['jwt_token']

		func = Mock(return_value=JsonResponse({'status': 'ok'}))
		decorated_func = required_jwt_auth(func)

		# No token
		request = HttpRequest()
		response = decorated_func(request)
		self.assertEqual(response.status_code, 400)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Missed auth token'})

		# Token valid
		request = HttpRequest()
		request.META['HTTP_JWT_TOKEN'] = jwt_token
		response = decorated_func(request)
		self.assertEqual(response.status_code, 200)
		self.assertJSONEqual(response.content, {'status': 'ok'})

		# Invalid token
		request = HttpRequest()
		request.META['HTTP_JWT_TOKEN'] = 'invalid'
		response = decorated_func(request)
		self.assertEqual(response.status_code, 403)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid token'})

		# Invalid sid
		request = HttpRequest()
		request.META['HTTP_JWT_TOKEN'] = jwt.encode({'sid': 999}, settings.JWT_SECRET_KEY, algorithm='HS256')
		response = decorated_func(request)
		self.assertEqual(response.status_code, 403)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid credentials'})

	def test_password_change(self):
		subs = Subscriptor.objects.create_subscriptor('me@me.com', 'pass')

		payload = {'email': 'me@me.com', 'password': 'pass'}
		response = self.client.post('/auth/', json.dumps(payload), content_type="application/json")
		jwt_token = json.loads(response.content)['jwt_token']

		# Valid password
		payload = {
			'old_password': 'pass',
			'new_password': 'new_pass',
		}
		response = self.client.post('/password_change/', json.dumps(payload), content_type="application/json", HTTP_JWT_TOKEN=jwt_token)
		self.assertEqual(response.status_code, 200)
		expected_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJoIjoiODk0NDRlOTdjOGJjNWY1MzIwNTc4NzQxMzE5MWZkOWMzMDdhNWM4NmQwYzAyNTAyMDM4NTA2NjU4MGU2MGU0MCIsInNpZCI6Mn0.gPOtVn_puKckqjqautfuqsvWNswhhIGhh0ZNElqcAng'
		self.assertJSONEqual(response.content, {'status': 'ok',	'jwt_token': expected_token})
		self.assertTrue(response.has_header('JWT_TOKEN'))
		self.assertEqual(response._headers['jwt_token'][1], expected_token)

		self.assertEqual(login('me@me.com', 'new_pass'), subs)
		with self.assertRaises(InvalidCredentials):
			login('me@me.com', 'pass')

		# Login with the old jwt_token (invalid)
		with self.assertRaises(InvalidCredentials):
			validate_jwt(jwt_token)

		# Relogin
		payload = {'email': 'me@me.com', 'password': 'new_pass'}
		response = self.client.post('/auth/', json.dumps(payload), content_type="application/json")
		new_jwt_token = json.loads(response.content)['jwt_token']

		# No credentials
		payload = {}
		response = self.client.post('/password_change/', json.dumps(payload), content_type="application/json", HTTP_JWT_TOKEN=new_jwt_token)
		self.assertEqual(response.status_code, 400)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid request'})

		# Invalid password
		payload = {
			'old_password': 'err',
			'new_password': 'new_new_pass',
		}
		response = self.client.post('/password_change/', json.dumps(payload), content_type="application/json", HTTP_JWT_TOKEN=new_jwt_token)
		self.assertEqual(response.status_code, 403)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid credentials'})
		self.assertEqual(login('me@me.com', 'new_pass'), subs)
		with self.assertRaises(InvalidCredentials):
			login('me@me.com', 'new_new_pass')

	def test_password_reset(self):
		subs = Subscriptor.objects.create_subscriptor('me@me.com', 'pass')

		# Valid email
		payload = {
			'email': 'me@me.com',
		}
		response = self.client.post('/password_reset/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 200)
		self.assertEquals(len(mail.outbox), 1)
		self.assertEquals(mail.outbox[0].subject, 'Restablecimiento de contraseña en Aragón Open SocialData')
		self.assertEquals(mail.outbox[0].to, ['me@me.com'])
		mail.outbox = []

		# No email
		payload = {}
		response = self.client.post('/password_reset/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 400)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid request'})
		self.assertEquals(len(mail.outbox), 0)

		# Invalid email (fails silently)
		payload = {
			'email': 'donotexists@no.com',
		}
		response = self.client.post('/password_reset/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 200)
		self.assertEquals(len(mail.outbox), 0)

	def test_password_reset_confirm(self):
		subs = Subscriptor.objects.create_subscriptor('me@me.com', 'pass')
		sidb64 = base64.urlsafe_b64encode(str(subs.id))
		token = token_generator.make_token(subs)
		token_wt_sidb64 = '%s=-%s' % (sidb64, token)

		# Valid email
		payload = {
			't': token_wt_sidb64,
			'new_password': 'new_pass'
		}
		response = self.client.post('/password_reset_confirm/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 200)
		self.assertEqual(login('me@me.com', 'new_pass'), subs)
		with self.assertRaises(InvalidCredentials):
			login('me@me.com', 'pass')

		# No credentials
		payload = {}
		response = self.client.post('/password_reset_confirm/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 400)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid request'})

		# Reuse the same token after change the password
		payload = {
			't': token_wt_sidb64,
			'new_password': 'new_new_pass',
		}
		response = self.client.post('/password_reset_confirm/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 403)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid reset link'})
		with self.assertRaises(InvalidCredentials):
			login('me@me.com', 'new_new_pass')

		# Reuse the token after login -> if I can do login I remember the password -> invalidate
		token = token_generator.make_token(subs)
		token_wt_sidb64 = '%s=-%s' % (sidb64, token)
		self.assertEqual(login('me@me.com', 'new_pass'), subs)
		payload = {
			't': token_wt_sidb64,
			'new_password': 'new_new_pass'
		}
		response = self.client.post('/password_reset_confirm/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 403)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid reset link'})
		with self.assertRaises(InvalidCredentials):
			login('me@me.com', 'new_new_pass')

		# Invalid token
		payload = {
			't': token,
			'new_password': 'new_new_pass',
		}
		response = self.client.post('/password_reset_confirm/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 403)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid reset link'})

		payload['t'] = 'none=-'
		response = self.client.post('/password_reset_confirm/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 403)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid reset link'})

		payload['t'] = '=-none'
		response = self.client.post('/password_reset_confirm/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 403)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid reset link'})

		payload['t'] = True
		response = self.client.post('/password_reset_confirm/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 403)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid reset link'})

		payload['t'] = 132
		response = self.client.post('/password_reset_confirm/', json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 403)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid reset link'})


class TestSubscriptions(TestCase):
	def setUp(self):
		Term.objects.all().delete()
		Subscription.objects.all().delete()
		Subscriptor.objects.all().delete()


	def test_subscribe(self):
		subs = Subscriptor.objects.create_subscriptor('me@me.com', 'pass')

		payload = {'email': 'me@me.com', 'password': 'pass'}
		response = self.client.post('/auth/', json.dumps(payload), content_type="application/json")
		jwt_token = json.loads(response.content)['jwt_token']

		# Valid subscription
		payload = {
			'subscriptions': [
				{'name': 'test1', 'region': 'region1', 'terms': ['one', 'two']},
				{'name': 'test2', 'region': 'region2', 'terms': ['three', 'four']},
				{'name': 'test3', 'region': 'region3', 'terms': ['three', 'five']},
			]
		}
		response = self.client.post('/subscribe/', json.dumps(payload), content_type="application/json", HTTP_JWT_TOKEN=jwt_token)
		self.assertEqual(response.status_code, 200)
		self.assertJSONEqual(response.content, {'status': 'ok'})

		self.assertEqual(Subscription.objects.filter(subscriptor=subs).count(), 3)

		# Empty
		payload = {
			'subscriptions': [
				{'name': 'test1', 'region': 'region1', 'terms': ['one', 'two']},
				{'name': 'test2', 'region': 'region2', 'terms': []},
				{'name': 'test3', 'region': 'region3', 'terms': ['three', 'five']},
			]
		}
		response = self.client.post('/subscribe/', json.dumps(payload), content_type="application/json", HTTP_JWT_TOKEN=jwt_token)
		self.assertEqual(response.status_code, 400)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Empty subscription'})


	def test_change_subscription(self):
		subs = Subscriptor.objects.create_subscriptor('me@me.com', 'pass')
		s1 = Subscription.objects.create(subscriptor=subs, name='test1', region='region1')
		s2 = Subscription.objects.create(subscriptor=subs, name='test2', region='region2')
		s3 = Subscription.objects.create(subscriptor=subs, name='test3', region='region3')
		Term.objects.create(subscription=s1, term='term1')
		Term.objects.create(subscription=s2, term='term2')
		Term.objects.create(subscription=s3, term='term3')

		payload = {'email': 'me@me.com', 'password': 'pass'}
		response = self.client.post('/auth/', json.dumps(payload), content_type="application/json")
		jwt_token = json.loads(response.content)['jwt_token']

		# Valid subscription
		payload = {
			'subscriptions': [
				{'name': 'test99', 'region': 'region99', 'terms': ['term99']},
				{'name': 'test22', 'region': 'region22', 'terms': ['term22']},
			]
		}
		response = self.client.post('/subscribe/', json.dumps(payload), content_type="application/json", HTTP_JWT_TOKEN=jwt_token)
		self.assertEqual(response.status_code, 200)
		self.assertJSONEqual(response.content, {'status': 'ok'})
		self.assertEqual(subs.subscriptions.all().count(), 2)
		self.assertEqual(subs.subscriptions.first().name, 'test99')
		self.assertEqual(subs.subscriptions.first().region, 'region99')
		self.assertEqual(subs.subscriptions.first().terms.first().term, 'term99')
		self.assertEqual(subs.subscriptions.last().name, 'test22')
		self.assertEqual(subs.subscriptions.last().region, 'region22')
		self.assertEqual(subs.subscriptions.last().terms.first().term, 'term22')

		# Empty
		payload = {
			'subscriptions': [
				{'name': 'test1', 'region': 'region1', 'terms': ['one', 'two']},
				{'name': 'test2', 'region': 'region2', 'terms': []},
				{'name': 'test3', 'region': 'region3', 'terms': ['three', 'five']},
			]
		}
		response = self.client.post('/subscribe/', json.dumps(payload), content_type="application/json", HTTP_JWT_TOKEN=jwt_token)
		self.assertEqual(response.status_code, 400)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Empty subscription'})


	def test_get_subscriptions(self):
		subs = Subscriptor.objects.create_subscriptor('me@me.com', 'pass')
		s1 = Subscription.objects.create(subscriptor=subs, name='test1', region='region1')
		s2 = Subscription.objects.create(subscriptor=subs, name='test2', region='region2')
		s3 = Subscription.objects.create(subscriptor=subs, name='test3', region='region3')
		Term.objects.create(subscription=s1, term='term1')
		Term.objects.create(subscription=s2, term='term2')
		Term.objects.create(subscription=s3, term='term3')

		payload = {'email': 'me@me.com', 'password': 'pass'}
		response = self.client.post('/auth/', json.dumps(payload), content_type="application/json")
		jwt_token = json.loads(response.content)['jwt_token']

		response = self.client.get('/get_subscriptions/', content_type="application/json", HTTP_JWT_TOKEN=jwt_token)
		self.assertEqual(response.status_code, 200)
		self.assertJSONEqual(response.content, {
			'status': 'ok',
			'subscriptions': [
				{'name': 'test3', 'region': 'region3', 'terms': ['term3']},
				{'name': 'test2', 'region': 'region2', 'terms': ['term2']},
				{'name': 'test1', 'region': 'region1', 'terms': ['term1']},
			]
		})

		# Empty
		subs2 = Subscriptor.objects.create_subscriptor('other@other.com', 'secret')
		payload = {'email': 'other@other.com', 'password': 'secret'}
		response = self.client.post('/auth/', json.dumps(payload), content_type="application/json")
		jwt_token = json.loads(response.content)['jwt_token']

		response = self.client.get('/get_subscriptions/', content_type="application/json", HTTP_JWT_TOKEN=jwt_token)
		self.assertEqual(response.status_code, 200)
		self.assertJSONEqual(response.content, {'status': 'ok', 'subscriptions': []})


	def test_cancel_subscription(self):
		subs = Subscriptor.objects.create_subscriptor('me@me.com', 'pass')
		s1 = Subscription.objects.create(subscriptor=subs, name='test1', region='region1')
		s2 = Subscription.objects.create(subscriptor=subs, name='test2', region='region2')
		s3 = Subscription.objects.create(subscriptor=subs, name='test3', region='region3')
		Term.objects.create(subscription=s1, term='term1')
		Term.objects.create(subscription=s2, term='term2')
		Term.objects.create(subscription=s3, term='term3')

		payload = {'email': 'me@me.com', 'password': 'pass'}
		response = self.client.post('/auth/', json.dumps(payload), content_type="application/json")
		jwt_token = json.loads(response.content)['jwt_token']

		# Valid subscription
		self.assertEqual(Subscriptor.objects.filter(email='me@me.com').count(), 1)
		response = self.client.delete('/cancel_subscription/', content_type="application/json", HTTP_JWT_TOKEN=jwt_token)
		self.assertEqual(response.status_code, 200)
		self.assertJSONEqual(response.content, {'status': 'ok'})
		self.assertEqual(Subscriptor.objects.filter(email='me@me.com').count(), 0)
		self.assertEqual(Subscription.objects.filter(subscriptor__email='me@me.com').count(), 0)
		self.assertEqual(Subscription.objects.all().count(), 0)

		# Subscriptor does not exist
		response = self.client.delete('/cancel_subscription/', content_type="application/json", HTTP_JWT_TOKEN=jwt_token)
		self.assertEqual(response.status_code, 403)
		self.assertJSONEqual(response.content, {'status': 'nok', 'error': 'Invalid credentials'})
		self.assertEqual(Subscriptor.objects.filter(email='me@me.com').count(), 0)
