# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0004_auto_20150422_2306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addressforwarding',
            name='coin_symbol',
            field=models.CharField(db_index=True, max_length=16, choices=[('btc', 'Bitcoin'), ('btc-testnet', 'Bitcoin Testnet'), ('ltc', 'Litecoin'), ('doge', 'Dogecoin'), ('bcy', 'BlockCypher Testnet')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='addresssubscription',
            name='coin_symbol',
            field=models.CharField(db_index=True, max_length=16, choices=[('btc', 'Bitcoin'), ('btc-testnet', 'Bitcoin Testnet'), ('ltc', 'Litecoin'), ('doge', 'Dogecoin'), ('bcy', 'BlockCypher Testnet')]),
            preserve_default=True,
        ),
    ]
