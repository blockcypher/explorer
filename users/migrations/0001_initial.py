# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', default=django.utils.timezone.now)),
                ('date_joined', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('first_name', models.CharField(null=True, blank=True, max_length=64)),
                ('last_name', models.CharField(null=True, blank=True, max_length=64)),
                ('email', models.EmailField(unique=True, max_length=128)),
                ('is_active', models.BooleanField(help_text='Can login?', default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('creation_ip', models.IPAddressField(db_index=True)),
                ('creation_user_agent', models.CharField(blank=True, db_index=True, max_length=1024)),
                ('email_verified', models.BooleanField(default=False, db_index=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LoggedLogin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('login_at', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ip_address', models.IPAddressField(db_index=True)),
                ('user_agent', models.CharField(blank=True, db_index=True, max_length=1024)),
                ('auth_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
