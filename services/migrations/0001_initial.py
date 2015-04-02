# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='APICall',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('api_name', models.CharField(max_length=3, db_index=True)),
                ('url_hit', models.URLField(max_length=1024, db_index=True)),
                ('response_code', models.PositiveSmallIntegerField(db_index=True)),
                ('post_params', jsonfield.fields.JSONField(blank=True, null=True)),
                ('headers', models.CharField(max_length=2048, blank=True, null=True)),
                ('api_results', models.CharField(max_length=100000, blank=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WebHook',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ip_address', models.IPAddressField(db_index=True)),
                ('user_agent', models.CharField(max_length=1024, blank=True, db_index=True)),
                ('api_name', models.CharField(max_length=3, db_index=True, choices=[('BAN', 'blockcypher address notification')])),
                ('hostname', models.CharField(max_length=512, db_index=True)),
                ('request_path', models.CharField(max_length=2048, db_index=True)),
                ('uses_https', models.BooleanField(default=False, db_index=True)),
                ('succeeded', models.BooleanField(default=False, db_index=True)),
                ('data_from_get', jsonfield.fields.JSONField(blank=True, null=True)),
                ('data_from_post', jsonfield.fields.JSONField(blank=True, null=True)),
                ('address_subscription', models.ForeignKey(to='addresses.AddressSubscription', blank=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
