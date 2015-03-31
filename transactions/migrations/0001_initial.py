# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OnChainTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('tx_hash', models.CharField(db_index=True, max_length=128)),
                ('conf_num', models.IntegerField(db_index=True)),
                ('double_spend', models.BooleanField(db_index=True, default=False)),
                ('satoshis_sent', models.BigIntegerField(db_index=True)),
                ('fee_in_satoshis', models.BigIntegerField(db_index=True)),
                ('address_subscription', models.ForeignKey(to='addresses.AddressSubscription')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
