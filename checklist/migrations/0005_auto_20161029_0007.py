# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checklist', '0004_auto_20161028_2313'),
    ]

    operations = [
        migrations.CreateModel(
            name='assignedToMe',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name_plural': 'Assigned to me',
            },
            bases=('checklist.assignedtask',),
        ),
        migrations.CreateModel(
            name='myTask',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('checklist.assignedtask',),
        ),
        migrations.RemoveField(
            model_name='assignedtask',
            name='awaiting_feedback',
        ),
    ]
