# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SentEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sent_at', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('from_email', models.EmailField(db_index=True, max_length=256)),
                ('from_name', models.CharField(blank=True, max_length=256, db_index=True, null=True)),
                ('to_email', models.EmailField(db_index=True, max_length=256)),
                ('to_name', models.CharField(blank=True, max_length=256, db_index=True, null=True)),
                ('cc_email', models.EmailField(blank=True, max_length=256, db_index=True, null=True)),
                ('cc_name', models.CharField(blank=True, max_length=256, db_index=True, null=True)),
                ('body_template', models.CharField(db_index=True, max_length=256)),
                ('body_context', jsonfield.fields.JSONField()),
                ('subject', models.TextField()),
                ('unsub_code', models.CharField(unique=True, db_index=True, max_length=64)),
                ('unsubscribed_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('unsub_ip', models.IPAddressField(blank=True, db_index=True, null=True)),
                ('unsub_ua', models.CharField(blank=True, db_index=True, max_length=1024)),
                ('verif_code', models.CharField(blank=True, max_length=64, unique=True, db_index=True, null=True)),
                ('verified_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('verif_ip', models.IPAddressField(blank=True, db_index=True, null=True)),
                ('verif_ua', models.CharField(blank=True, db_index=True, max_length=1024)),
                ('address_subscription', models.ForeignKey(blank=True, to='addresses.AddressSubscription', null=True)),
                ('auth_user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
