# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-11 01:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movieindex', '0006_moviefolder_default_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='moviefolder',
            name='last_scanned',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
