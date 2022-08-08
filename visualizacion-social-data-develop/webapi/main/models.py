# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone

import hashlib


"""
Simple User Model
"""


class InvalidCredentials(Exception): pass


def login(email, password):
	if not email:
		raise InvalidCredentials('The given email must be set')
	if not password:
		raise InvalidCredentials('The given password must be set')
	try:
		subscriptor = Subscriptor.objects.get(email=email)
	except Subscriptor.DoesNotExist:
		raise InvalidCredentials('Invalid credentials')
	if not subscriptor.check_password(password):
		raise InvalidCredentials('Invalid credentials')
	subscriptor.last_login = timezone.now()
	subscriptor.save(update_fields=['last_login'])
	return subscriptor


class SubscriptorManager(models.Manager):
	@classmethod
	def normalize_email(cls, email):
		"""
		Normalize the email address by lowercasing the domain part of the it.
		"""
		email = email or ''
		try:
			email_name, domain_part = email.strip().rsplit('@', 1)
		except ValueError:
			pass
		else:
			email = '@'.join([email_name, domain_part.lower()])
		return email

	def create_subscriptor(self, email, password, **extra_fields):
		"""
		Creates and saves a Subscriptor with the given email and password.
		"""
		if not email:
			raise ValueError('The given email must be set')
		if not password:
			raise ValueError('The given password must be set')
		if self.model.objects.filter(email=email).exists():
			raise ValueError('The email is yet registered')
		email = self.normalize_email(email)
		subscriptor = self.model(email=email, **extra_fields)
		subscriptor.set_password(password)
		subscriptor.save()
		return subscriptor


class Subscriptor(models.Model):
	email = models.EmailField('Email', unique=True, editable=False)
	password = models.CharField('Password', max_length=128)
	created_at = models.DateTimeField('Created at', default=timezone.now)
	last_login = models.DateTimeField('Last login', blank=True, null=True)

	objects = SubscriptorManager()

	def __init__(self, *args, **kwargs):
		super(Subscriptor, self).__init__(*args, **kwargs)
		self._password_setted = False

	def make_password(self, raw_password):
		return hashlib.md5(raw_password).hexdigest()

	def set_password(self, raw_password):
		self.password = self.make_password(raw_password)
		self._password_setted = True

	def check_password(self, raw_password):
		if raw_password is None:
			raise ValueError('Password must not be null')
		return self.password == self.make_password(raw_password)

	def change_password(self, old_password, new_raw_password):
		""" Return True if the password validation is ok. """
		if not self.check_password(old_password):
			return False
		self.set_password(new_raw_password)
		self.save()
		return True

	def save(self, *args, **kwargs):
		if self._password_setted:
			self._password_setted = False
		super(Subscriptor, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.email


class Subscription(models.Model):
	subscriptor = models.ForeignKey(Subscriptor, related_name='subscriptions')
	name = models.CharField('Nombre', max_length=150)
	region = models.CharField('Región', max_length=50)

	def __unicode__(self):
		return u'{0}_{1}'.format(self.subscriptor, self.name)


class Term(models.Model):
	subscription = models.ForeignKey(Subscription, related_name='terms')
	term = models.CharField('Término', max_length=150)

	def __unicode__(self):
		return u'{0}_{1}'.format(self.subscription, self.term)
