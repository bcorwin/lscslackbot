# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('checklist', '0003_auto_20161028_2302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignedtask',
            name='assigned_to',
            field=models.ForeignKey(related_name='assignee', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
