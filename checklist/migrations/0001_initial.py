# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='assignedTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('completed', models.BooleanField(default=False)),
                ('inserted_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(related_name='approvedby', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Checklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=64)),
                ('dmc_default', models.BooleanField(default=False)),
                ('ia_default', models.BooleanField(default=False)),
                ('inserted_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(max_length=1024)),
                ('inserted_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('task', models.ForeignKey(to='checklist.assignedTask')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(default=b'', max_length=1024)),
                ('result', models.CharField(max_length=1, choices=[(b'A', b'Approve'), (b'D', b'Deny')])),
                ('inserted_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(related_name='assigned_to', to=settings.AUTH_USER_MODEL)),
                ('requestor', models.ForeignKey(related_name='requestor', to=settings.AUTH_USER_MODEL)),
                ('task', models.OneToOneField(to='checklist.assignedTask')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(max_length=128)),
                ('inserted_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('checklist', models.ForeignKey(to='checklist.Checklist')),
            ],
        ),
        migrations.AddField(
            model_name='assignedtask',
            name='task',
            field=models.ForeignKey(to='checklist.Task'),
        ),
        migrations.AddField(
            model_name='assignedtask',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
