# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressSubscription',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('coin_symbol', models.CharField(db_index=True, choices=[('btc', 'Bitcoin'), ('btc-testnet', 'Bitcoin Testnet'), ('ltc', 'Litecoin'), ('doge', 'Dogecoin'), ('uro', 'Uro'), ('bcy', 'BlockCypher Testnet')], max_length=16)),
                ('b58_address', models.CharField(db_index=True, max_length=64)),
                ('notify_on_broadcast', models.BooleanField(db_index=True, default=True)),
                ('notify_on_first_confirm', models.BooleanField(db_index=True, default=True)),
                ('notify_on_sixth_confirm', models.BooleanField(db_index=True, default=False)),
                ('notify_on_deposit', models.BooleanField(db_index=True, default=True)),
                ('notify_on_withdrawal', models.BooleanField(db_index=True, default=True)),
                ('blockcypher_id', models.CharField(db_index=True, choices=[('btc', 'Bitcoin'), ('btc-testnet', 'Bitcoin Testnet'), ('ltc', 'Litecoin'), ('doge', 'Dogecoin'), ('uro', 'Uro'), ('bcy', 'BlockCypher Testnet')], max_length=64)),
                ('auth_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
