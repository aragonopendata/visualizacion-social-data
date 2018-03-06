# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings

from django.contrib.auth.tokens import PasswordResetTokenGenerator

from django.template import loader
from django.core.mail import EmailMultiAlternatives

from main.models import Subscriptor, InvalidCredentials, login

import jwt
import hashlib
import base64

import json


"""
Custom JWT Auth
"""

token_generator = PasswordResetTokenGenerator()


def create_jwt(subscriptor):
	jwtbody = {
		'sid': subscriptor.id,
		'h': hashlib.sha256(subscriptor.password).hexdigest(),
	}
	jwttoken = jwt.encode(jwtbody, settings.JWT_SECRET_KEY, algorithm='HS256')
	return jwttoken


def validate_jwt(jwttoken):
	jwtbody = jwt.decode(jwttoken, settings.JWT_SECRET_KEY, algorithms=['HS256'])
	subscriptor = Subscriptor.objects.get(pk=jwtbody['sid'])
	if jwtbody['h'] != hashlib.sha256(subscriptor.password).hexdigest():
		raise InvalidCredentials
	return subscriptor


def send_mail(subject, from_email, to_email, email_template_name, context):
	"""
	Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
	"""
	body = loader.render_to_string(email_template_name, context)
	email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
	email_message.send()


def ensure_json_body(view_func):
	"""
	Decorator to ensure the request has a JSON object in the body.
	"""
	def _wrapped_view(request, *args, **kwargs):
		try:
			params = json.loads(request.body)
		except (TypeError, ValueError):
			return JsonResponse({'status': 'nok', 'error': 'Invalid request'}, status=400)
		return view_func(request, params, *args, **kwargs)
	return _wrapped_view


def required_jwt_auth(view_func):
	"""
	Decorator to validate the JWT token given in the headers and inject the subscriptor
	instance in the request object.
	"""
	def _wrapped_view(request, *args, **kwargs):
		try:
			request.subscriptor = validate_jwt(request.META['HTTP_JWT_TOKEN'])
		except KeyError:
			return JsonResponse({'status': 'nok', 'error': 'Missed auth token'}, status=400)
		except (jwt.DecodeError, jwt.ExpiredSignature):
			return JsonResponse({'status': 'nok', 'error': 'Invalid token'}, status=403)
		except (Subscriptor.DoesNotExist, InvalidCredentials):
			return JsonResponse({'status': 'nok', 'error': 'Invalid credentials'}, status=403)
		return view_func(request, *args, **kwargs)
	return _wrapped_view


@require_http_methods(['POST'])
@ensure_json_body
def register(request, params):
	email = params.get('email', None)
	password = params.get('password', None)
	if not email or not password:
		return JsonResponse({'status': 'nok', 'error': 'Invalid request'}, status=400)
	try:
		subscriptor = Subscriptor.objects.create_subscriptor(email=email, password=password)
	except ValueError as exc:
		return JsonResponse({'status': 'nok', 'error': exc.message}, status=400)
	return JsonResponse({'status': 'ok'})


@require_http_methods(['POST'])
@ensure_json_body
def auth(request, params):
	"""
	Auth view
	"""
	email = params.get('email', None)
	password = params.get('password', None)

	try:
		subscriptor = login(email, password)
	except InvalidCredentials:
		return JsonResponse({'status': 'nok', 'error': 'Invalid credentials'}, status=403)

	jwttoken = create_jwt(subscriptor)
	response = JsonResponse({'status': 'ok', 'jwt_token': jwttoken})
	response['JWT_TOKEN'] = jwttoken
	return response


@require_http_methods(['POST'])
@required_jwt_auth
@ensure_json_body
def password_change(request, params):
	"""
	Password change view and invalidate the jwt token
	"""
	old_password = params.get('old_password', None)
	new_password = params.get('new_password', None)

	if not old_password or not new_password:
		return JsonResponse({'status': 'nok', 'error': 'Invalid request'}, status=400)
	try:
		if not request.subscriptor.change_password(old_password, new_password):
			return JsonResponse({'status': 'nok', 'error': 'Invalid credentials'}, status=403)
	except ValueError as exc:
		return JsonResponse({'status': 'nok', 'error': 'Invalid credentials'}, status=403)

	jwttoken = create_jwt(request.subscriptor)
	response = JsonResponse({'status': 'ok', 'jwt_token': jwttoken})
	response['JWT_TOKEN'] = jwttoken
	return response


@require_http_methods(['POST'])
@ensure_json_body
def password_reset(request, params):
	"""
	2 views for password reset (based on django.contrib.auth):
	 - password reset - sends the email
	"""
	email = params.get('email', None)

	if not email:
		return JsonResponse({'status': 'nok', 'error': 'Invalid request'}, status=400)
	try:
		subscriptor = Subscriptor.objects.get(email=email)
	except Subscriptor.DoesNotExist:
		return JsonResponse({'status': 'ok'}) # For security we do not send information that the email does not exist

	sidb64 = base64.urlsafe_b64encode(str(subscriptor.id))
	token = token_generator.make_token(subscriptor)
	token_wt_sidb64 = '%s=-%s' % (sidb64, token)
	context = {
		'subscriptor': subscriptor,
		'token': token_wt_sidb64,
	}
	send_mail(
		subject='Restablecimiento de contraseña en Aragón Open SocialData',
		from_email=settings.EMAIL_FROM_EMAIL,
		to_email=subscriptor.email,
		email_template_name='mail/password_reset_email.html',
		context=context,
	)
	return JsonResponse({'status': 'ok'})


@require_http_methods(['POST'])
@ensure_json_body
def password_reset_confirm(request, params):
	token_wt_sidb64 = params.get('t', None)
	new_password = params.get('new_password', None)

	if not token_wt_sidb64 or not new_password:
		return JsonResponse({'status': 'nok', 'error': 'Invalid request'}, status=400)

	try:
		if '=-' not in token_wt_sidb64:
			raise ValueError('Invalid token')
		sidb64, token = token_wt_sidb64.split('=-')
		if not sidb64 or not token:
			raise ValueError('Invalid token')
		sid = int(base64.urlsafe_b64decode(str(sidb64)))
	except (AttributeError, TypeError, ValueError, UnicodeEncodeError):
		return JsonResponse({'status': 'nok', 'error': 'Invalid reset link'}, status=403)

	try:
		subscriptor = Subscriptor.objects.get(pk=sid)
	except Subscriptor.DoesNotExist:
		subscriptor = None

	if subscriptor is not None and token_generator.check_token(subscriptor, token):
		subscriptor.set_password(new_password)
		subscriptor.save()
		return JsonResponse({'status': 'ok'})
	else:
		return JsonResponse({'status': 'nok', 'error': 'Invalid reset link'}, status=403)
