# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checklist', '0005_auto_20161105_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignedtask',
            name='assigned_checklist',
            field=models.ForeignKey(to='checklist.assignedChecklist'),
        ),
    ]
