# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('checklist', '0002_assignedtasks'),
    ]

    operations = [
        migrations.CreateModel(
            name='assignedTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('completed', models.BooleanField(default=False)),
                ('awaiting_feedback', models.BooleanField(default=False)),
                ('inserted_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(related_name='assignee', to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(to='checklist.Task')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='assignedtasks',
            name='assigned_to',
        ),
        migrations.RemoveField(
            model_name='assignedtasks',
            name='task',
        ),
        migrations.RemoveField(
            model_name='assignedtasks',
            name='user',
        ),
        migrations.DeleteModel(
            name='assignedTasks',
        ),
    ]
