# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0002_addresssubscription_unsubscribed_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addresssubscription',
            name='blockcypher_id',
            field=models.CharField(max_length=64, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='addresssubscription',
            name='notify_on_first_confirm',
            field=models.BooleanField(default=False, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='addresssubscription',
            name='notify_on_sixth_confirm',
            field=models.BooleanField(default=True, db_index=True),
            preserve_default=True,
        ),
    ]
