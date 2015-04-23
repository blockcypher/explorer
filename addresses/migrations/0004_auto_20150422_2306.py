# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('addresses', '0003_auto_20150331_1844'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressForwarding',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('archived_at', models.DateTimeField(db_index=True, blank=True, null=True)),
                ('coin_symbol', models.CharField(choices=[('btc', 'Bitcoin'), ('btc-testnet', 'Bitcoin Testnet'), ('ltc', 'Litecoin'), ('doge', 'Dogecoin'), ('uro', 'Uro'), ('bcy', 'BlockCypher Testnet')], db_index=True, max_length=16)),
                ('initial_address', models.CharField(db_index=True, max_length=64)),
                ('destination_address', models.CharField(db_index=True, max_length=64)),
                ('blockcypher_id', models.CharField(db_index=True, max_length=64)),
                ('auth_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='addresssubscription',
            name='address_forwarding_obj',
            field=models.ForeignKey(to='addresses.AddressForwarding', null=True, blank=True),
            preserve_default=True,
        ),
    ]
