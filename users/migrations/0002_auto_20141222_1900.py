# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='authuser',
            name='first_name',
            field=models.CharField(max_length=64, blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authuser',
            name='is_superuser',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authuser',
            name='last_name',
            field=models.CharField(max_length=64, blank=True, null=True),
            preserve_default=True,
        ),
    ]
