# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionEvent',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('tx_hash', models.CharField(db_index=True, max_length=128)),
                ('b58_address', models.CharField(db_index=True, max_length=64)),
                ('address_subscription', models.ForeignKey(to='addresses.AddressSubscription')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
