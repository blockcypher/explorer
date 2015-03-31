# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0001_initial'),
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentemail',
            name='transaction_event',
            field=models.ForeignKey(blank=True, to='transactions.OnChainTransaction', null=True),
            preserve_default=True,
        ),
    ]
