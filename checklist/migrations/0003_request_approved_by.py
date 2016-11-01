# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('checklist', '0002_auto_20161101_0011'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='approved_by',
            field=models.ForeignKey(related_name='approved_by', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
