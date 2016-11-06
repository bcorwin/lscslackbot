# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('checklist', '0006_auto_20161105_1917'),
    ]

    operations = [
        migrations.CreateModel(
            name='approvalGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inserted_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('checklist', models.ForeignKey(to='checklist.Checklist')),
                ('group', models.ForeignKey(to='auth.Group')),
            ],
        ),
    ]
