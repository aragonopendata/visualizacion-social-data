# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name=b'Nombre')),
                ('region', models.CharField(max_length=50, verbose_name=b'Regi\xc3\xb3n')),
            ],
        ),
        migrations.CreateModel(
            name='Subscriptor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(verbose_name=b'Email', unique=True, max_length=254, editable=False)),
                ('password', models.CharField(max_length=128, verbose_name=b'Password')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'Created at')),
            ],
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('term', models.CharField(max_length=150, verbose_name=b'T\xc3\xa9rmino')),
                ('subscription', models.ForeignKey(related_name='terms', to='main.Subscription')),
            ],
        ),
        migrations.AddField(
            model_name='subscription',
            name='subscriptor',
            field=models.ForeignKey(related_name='subscriptions', to='main.Subscriptor'),
        ),
    ]
