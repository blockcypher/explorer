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
                ('email', models.EmailField(unique=True, max_length=128)),
                ('is_active', models.BooleanField(help_text='Can login?', default=True)),
                ('is_staff', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BlockypherToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created_at', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('email_used', models.EmailField(unique=True, max_length=128)),
                ('auth_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GithubProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('added_at', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('github_id', models.IntegerField(db_index=True)),
                ('github_created_at', models.DateTimeField(db_index=True)),
                ('github_updated_at', models.DateTimeField(db_index=True)),
                ('github_username', models.CharField(max_length=256, db_index=True)),
                ('primary_email', models.EmailField(unique=True, max_length=128)),
                ('full_name', models.CharField(blank=True, max_length=128, db_index=True)),
                ('followers_cnt', models.IntegerField(db_index=True)),
                ('following_cnt', models.IntegerField(db_index=True)),
                ('public_repo_cnt', models.IntegerField(db_index=True)),
                ('public_gists_cnt', models.IntegerField(db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LoggedLogin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('login_at', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ip_address', models.IPAddressField(db_index=True)),
                ('user_agent', models.CharField(blank=True, max_length=1024, db_index=True)),
                ('auth_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='authuser',
            name='github_profile',
            field=models.OneToOneField(null=True, to='users.GithubProfile', blank=True),
            preserve_default=True,
        ),
    ]
