# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20141222_1900'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlockcypherToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('email_used', models.EmailField(max_length=128, unique=True)),
                ('auth_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='blockyphertoken',
            name='auth_user',
        ),
        migrations.DeleteModel(
            name='BlockypherToken',
        ),
    ]
