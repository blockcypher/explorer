# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0002_auto_20150330_2148'),
    ]

    operations = [
        migrations.AddField(
            model_name='onchaintransaction',
            name='is_deposit',
            field=models.BooleanField(db_index=True, default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='onchaintransaction',
            name='is_withdrawal',
            field=models.BooleanField(db_index=True, default=False),
            preserve_default=True,
        ),
    ]
