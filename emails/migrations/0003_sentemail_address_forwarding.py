# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0004_auto_20150422_2306'),
        ('emails', '0002_sentemail_transaction_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentemail',
            name='address_forwarding',
            field=models.ForeignKey(blank=True, null=True, to='addresses.AddressForwarding'),
            preserve_default=True,
        ),
    ]
