# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='addresssubscription',
            name='unsubscribed_at',
            field=models.DateTimeField(db_index=True, blank=True, null=True),
            preserve_default=True,
        ),
    ]
