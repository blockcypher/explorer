# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('addresses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SentEmail',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('sent_at', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('from_email', models.EmailField(max_length=256, db_index=True)),
                ('from_name', models.CharField(max_length=256, blank=True, db_index=True, null=True)),
                ('to_email', models.EmailField(max_length=256, db_index=True)),
                ('to_name', models.CharField(max_length=256, blank=True, db_index=True, null=True)),
                ('cc_email', models.EmailField(max_length=256, blank=True, db_index=True, null=True)),
                ('cc_name', models.CharField(max_length=256, blank=True, db_index=True, null=True)),
                ('body_template', models.CharField(max_length=256, db_index=True)),
                ('body_context', jsonfield.fields.JSONField()),
                ('subject', models.TextField()),
                ('unsub_code', models.CharField(max_length=64, db_index=True, unique=True)),
                ('unsubscribed_at', models.DateTimeField(db_index=True, blank=True, null=True)),
                ('unsub_ip', models.IPAddressField(blank=True, db_index=True, null=True)),
                ('unsub_ua', models.CharField(max_length=1024, blank=True, db_index=True)),
                ('verif_code', models.CharField(blank=True, max_length=64, unique=True, db_index=True, null=True)),
                ('verified_at', models.DateTimeField(db_index=True, blank=True, null=True)),
                ('verif_ip', models.IPAddressField(blank=True, db_index=True, null=True)),
                ('verif_ua', models.CharField(max_length=1024, blank=True, db_index=True)),
                ('address_subscription', models.ForeignKey(blank=True, to='addresses.AddressSubscription', null=True)),
                ('auth_user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('transaction_event', models.ForeignKey(blank=True, to='transactions.TransactionEvent', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
