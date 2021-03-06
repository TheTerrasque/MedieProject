# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-18 23:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('movieindex', '0007_moviefolder_last_scanned'),
    ]

    operations = [
        migrations.CreateModel(
            name='MovieDownloadKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(db_index=True, max_length=50)),
                ('valid_until', models.DateTimeField()),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movieindex.Movie')),
            ],
        ),
    ]
