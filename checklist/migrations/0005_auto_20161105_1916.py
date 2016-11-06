# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checklist', '0004_assignedchecklist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignedtask',
            name='user',
        ),
        migrations.AddField(
            model_name='assignedtask',
            name='assigned_checklist',
            field=models.ForeignKey(blank=True, to='checklist.assignedChecklist', null=True),
        ),
    ]
