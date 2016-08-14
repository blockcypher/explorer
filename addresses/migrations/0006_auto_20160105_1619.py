# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0005_auto_20151031_2319'),
    ]

    operations = [
        migrations.AddField(
            model_name='addresssubscription',
            name='disabled_at',
            field=models.DateTimeField(null=True, blank=True, db_index=True, help_text='Admin disabled'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='addresssubscription',
            name='unsubscribed_at',
            field=models.DateTimeField(null=True, blank=True, db_index=True, help_text='User disabled'),
            preserve_default=True,
        ),
    ]
